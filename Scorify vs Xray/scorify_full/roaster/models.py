"""
Scorify — Models
All models in one place. Clean, no circular imports.
"""
import hashlib
import random
import string
import uuid
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify


# ═══════════════════════════════════════════════════════════════════════════
# USER PROFILE
# ═══════════════════════════════════════════════════════════════════════════

class UserProfile(models.Model):
  PLAN_FREE = 'free'
  PLAN_PRO = 'pro'
  PLAN_VIP = 'vip'
  PLAN_CHOICES = [(PLAN_FREE,'Free'),(PLAN_PRO,'Pro'),(PLAN_VIP,'VIP')]

  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
  plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default=PLAN_FREE)
  pro_since = models.DateTimeField(null=True, blank=True)
  pro_expires = models.DateTimeField(null=True, blank=True)
  total_uploads = models.IntegerField(default=0)
  avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
  job_title = models.CharField(max_length=100, blank=True)
  industry = models.CharField(max_length=100, blank=True)
  bio = models.TextField(blank=True, max_length=300)
  career_goal = models.CharField(max_length=200, blank=True)
  skills_tags = models.TextField(blank=True)
  best_score = models.IntegerField(default=0)
  public_profile = models.BooleanField(default=False)
  onboarding_done = models.BooleanField(default=False)
  bonus_uploads = models.IntegerField(default=0) # earned via referrals
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f'{self.user.username} — {self.plan.upper()}'

  # ── Plan properties ──────────────────────────────────────────────────
  @property
  def is_pro(self):
    return self.plan in (self.PLAN_PRO, self.PLAN_VIP)

  @property
  def is_vip(self):
    return self.plan == self.PLAN_VIP

  @property
  def plan_badge(self):
    return {'free':'⚪','pro':'🔵','vip':''}.get(self.plan,'⚪')

  @property
  def plan_color(self):
    return {'free':'#64748b','pro':'#3b82f6','vip':'#ff4d00'}.get(self.plan,'#64748b')

  @property
  def daily_limit(self):
    return {'free':3,'pro':999,'vip':999}.get(self.plan, 3)

  # ── Usage ────────────────────────────────────────────────────────────
  @property
  def uploads_today(self):
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return CVAnalysis.objects.filter(user=self.user, created_at__gte=today).count()

  @property
  def can_upload(self):
    if self.bonus_uploads > 0:
      return True
    return self.uploads_today < self.daily_limit

  @property
  def uploads_remaining_today(self):
    if self.plan != self.PLAN_FREE:
      return 999
    base = max(0, 3 - self.uploads_today)
    return base + self.bonus_uploads

  # ── Profile ──────────────────────────────────────────────────────────
  @property
  def profile_completion(self):
    fields = [self.user.first_name, self.job_title, self.industry,
         self.bio, self.career_goal, self.skills_tags]
    filled = sum(1 for f in fields if f)
    has_avatar = 1 if self.avatar else 0
    return int(((filled + has_avatar) / (len(fields) + 1)) * 100)

  @property
  def score_trend(self):
    scores = list(
      CVAnalysis.objects.filter(user=self.user, overall_score__isnull=False)
      .order_by('-created_at')[:2]
      .values_list('overall_score', flat=True)
    )
    if len(scores) < 2:
      return 'neutral'
    return 'up' if scores[0] > scores[1] else ('down' if scores[0] < scores[1] else 'neutral')

  @property
  def achievements(self):
    badges = []
    if self.total_uploads >= 1: badges.append({'icon':'','name':'First Scan','desc':'Uploaded first CV'})
    if self.total_uploads >= 5: badges.append({'icon':'💪','name':'Scan Veteran','desc':'5 CVs analyzed'})
    if self.total_uploads >= 10: badges.append({'icon':'🏆','name':'Scan Master','desc':'10 CVs analyzed'})
    if self.total_uploads >= 25: badges.append({'icon':'👑','name':'Scan Legend','desc':'25 CVs analyzed'})
    if self.best_score >= 70: badges.append({'icon':'⭐','name':'High Scorer','desc':'Score 70+'})
    if self.best_score >= 85: badges.append({'icon':'💎','name':'Elite CV','desc':'Score 85+'})
    if self.best_score >= 95: badges.append({'icon':'🚀','name':'Perfect CV','desc':'Score 95+'})
    if self.plan == 'pro': badges.append({'icon':'🔵','name':'Pro Member','desc':'Upgraded to Pro'})
    if self.plan == 'vip': badges.append({'icon':'','name':'VIP Member','desc':'Elite VIP status'})
    if self.profile_completion >= 80: badges.append({'icon':'✅','name':'Complete Profile','desc':'Profile 80%'})
    referral = getattr(self, 'referral_code', None)
    if referral and getattr(referral, 'total_referrals', 0) >= 1:
      badges.append({'icon':'🤝','name':'Referrer','desc':'Referred a friend'})
    return badges


# ═══════════════════════════════════════════════════════════════════════════
# CV ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

class CVAnalysis(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='analyses')
  session_key = models.CharField(max_length=64, blank=True, null=True)
  original_filename = models.CharField(max_length=255)
  overall_score = models.IntegerField(null=True)
  verdict = models.CharField(max_length=100, blank=True)
  analysis_data = models.JSONField(null=True)
  is_preview = models.BooleanField(default=False)
  plan_used = models.CharField(max_length=10, default='free')
  created_at = models.DateTimeField(auto_now_add=True)
  processing_time = models.FloatField(null=True)
  ip_address = models.GenericIPAddressField(null=True)

  class Meta:
    ordering = ['-created_at']

  def __str__(self):
    u = self.user.username if self.user else 'Anonymous'
    return f'{u} — {self.original_filename} — {self.overall_score}/100'

  @property
  def score_class(self):
    if not self.overall_score:
      return 'neutral'
    if self.overall_score < 40:
      return 'fire'
    if self.overall_score < 65:
      return 'amber'
    return 'green'


# ═══════════════════════════════════════════════════════════════════════════
# CV CACHE — avoid re-analyzing identical CV text
# ═══════════════════════════════════════════════════════════════════════════

class CVCache(models.Model):
  cv_hash = models.CharField(max_length=64, unique=True, db_index=True)
  plan = models.CharField(max_length=10, default='free')
  analysis_data = models.JSONField()
  hit_count = models.IntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-created_at']

  def __str__(self):
    return f'Cache {self.cv_hash[:12]}… plan={self.plan} hits={self.hit_count}'

  @classmethod
  def get_hash(cls, cv_text: str, plan: str, job_desc: str = '') -> str:
    raw = f'{plan}::{job_desc[:200]}::{cv_text[:5000]}'
    return hashlib.sha256(raw.encode()).hexdigest()

  @classmethod
  def lookup(cls, cv_text: str, plan: str, job_desc: str = ''):
    h = cls.get_hash(cv_text, plan, job_desc)
    try:
      entry = cls.objects.get(cv_hash=h)
      # Expire after 7 days
      if timezone.now() - entry.created_at > timedelta(days=7):
        entry.delete()
        return None
      entry.hit_count += 1
      entry.save(update_fields=['hit_count'])
      return entry.analysis_data
    except cls.DoesNotExist:
      return None

  @classmethod
  def store(cls, cv_text: str, plan: str, job_desc: str, data: dict):
    h = cls.get_hash(cv_text, plan, job_desc)
    cls.objects.update_or_create(cv_hash=h, defaults={'plan': plan, 'analysis_data': data})


# ═══════════════════════════════════════════════════════════════════════════
# DB RATE LIMIT — replaces in-memory store (survives worker restarts)
# ═══════════════════════════════════════════════════════════════════════════

class RateLimitRecord(models.Model):
  ip = models.GenericIPAddressField(db_index=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-created_at']

  @classmethod
  def count(cls, ip: str, window_seconds: int) -> int:
    cutoff = timezone.now() - timedelta(seconds=window_seconds)
    return cls.objects.filter(ip=ip, created_at__gte=cutoff).count()

  @classmethod
  def add(cls, ip: str):
    cls.objects.create(ip=ip)

  @classmethod
  def cleanup(cls):
    """Remove records older than 2 hours. Call from management command."""
    cutoff = timezone.now() - timedelta(hours=2)
    cls.objects.filter(created_at__lt=cutoff).delete()


# ═══════════════════════════════════════════════════════════════════════════
# OTP CODE
# ═══════════════════════════════════════════════════════════════════════════

class OTPCode(models.Model):
  email = models.EmailField()
  code = models.CharField(max_length=6)
  created_at = models.DateTimeField(auto_now_add=True)
  is_used = models.BooleanField(default=False)
  pending_analysis_id = models.CharField(max_length=64, blank=True, null=True)

  class Meta:
    ordering = ['-created_at']

  def is_valid(self):
    return not self.is_used and timezone.now() < self.created_at + timedelta(minutes=10)

  @staticmethod
  def generate_code():
    return ''.join(random.choices(string.digits, k=6))

  def __str__(self):
    return f'{self.email} — {self.code} — {"used" if self.is_used else "active"}'


# ═══════════════════════════════════════════════════════════════════════════
# REFERRAL CODE
# ═══════════════════════════════════════════════════════════════════════════

class ReferralCode(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referral_code')
  code = models.CharField(max_length=12, unique=True, db_index=True)
  total_referrals = models.IntegerField(default=0)
  bonus_uploads_earned = models.IntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f'{self.user.username} → {self.code} ({self.total_referrals} refs)'

  @classmethod
  def generate_code(cls):
    chars = string.ascii_uppercase + string.digits
    while True:
      code = ''.join(random.choices(chars, k=8))
      if not cls.objects.filter(code=code).exists():
        return code

  @classmethod
  def get_or_create_for_user(cls, user):
    try:
      return user.referral_code
    except cls.DoesNotExist:
      return cls.objects.create(user=user, code=cls.generate_code())


class ReferralUse(models.Model):
  """Records each time a referral code was successfully used."""
  referral_code = models.ForeignKey(ReferralCode, on_delete=models.CASCADE, related_name='uses')
  referred_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referred_by')
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f'{self.referred_user.username} via {self.referral_code.code}'


# ═══════════════════════════════════════════════════════════════════════════
# SHARE CARD
# ═══════════════════════════════════════════════════════════════════════════

class ShareCard(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  analysis = models.ForeignKey(CVAnalysis, on_delete=models.CASCADE, related_name='share_cards')
  is_public = models.BooleanField(default=True)
  view_count = models.IntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f'Share {self.id} — {self.analysis.overall_score}/100'


# ═══════════════════════════════════════════════════════════════════════════
# BLOG POST
# ═══════════════════════════════════════════════════════════════════════════

class BlogPost(models.Model):
  title = models.CharField(max_length=200)
  slug = models.SlugField(unique=True, blank=True)
  excerpt = models.TextField(blank=True, max_length=300)
  content = models.TextField()
  cover_image = models.ImageField(upload_to='blog/', null=True, blank=True)
  tags = models.CharField(max_length=200, blank=True)
  author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
  published = models.BooleanField(default=False)
  view_count = models.IntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ['-created_at']

  def __str__(self):
    return self.title

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.title)
    super().save(*args, **kwargs)

  @property
  def tag_list(self):
    return [t.strip() for t in self.tags.split(',') if t.strip()]

  @property
  def read_time(self):
    words = len(self.content.split())
    return max(1, round(words / 200))


# ═══════════════════════════════════════════════════════════════════════════
# SIGNALS
# ═══════════════════════════════════════════════════════════════════════════

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
  if created:
    UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
  if hasattr(instance, 'profile'):
    try:
      instance.profile.save()
    except Exception:
      pass