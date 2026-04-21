"""
Scorify — Admin Panel
════════════════════════════
Custom Admin Site + Dashboard + Export CSV + OTP cleanup + Plan management.
All helpers are pure functions; no module-level DB calls.
"""

import csv
import json
from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import format_html
from django.db.models import Avg, Count

from .models import CVAnalysis, OTPCode, UserProfile


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS (pure functions — zero DB calls at import time)
# ═══════════════════════════════════════════════════════════════════════════

def score_badge(score):
  """Return a coloured HTML pill for a score value."""
  if score is None:
    return format_html('<span style="color:#555">—</span>')
  color = '#f87171' if score < 40 else ('#ffaa00' if score < 65 else '#4ade80')
  return format_html(
    '<span style="background:{c};color:#0a0804;padding:3px 10px;border-radius:99px;'
    'font-weight:800;font-size:12px;font-family:monospace">{s}</span>',
    c=color, s=score,
  )


def plan_badge(plan):
  """Return a coloured HTML pill for a plan name."""
  cfg = {
    'free': ('#64748b', '⚪', 'FREE'),
    'pro': ('#3b82f6', '🔵', 'PRO'),
    'vip': ('#ff4d00', '', 'VIP'),
  }
  color, icon, label = cfg.get(plan, ('#64748b', '⚪', plan.upper()))
  return format_html(
    '<span style="background:{c};color:white;padding:3px 12px;border-radius:99px;'
    'font-size:11px;font-weight:700">{i} {l}</span>',
    c=color, i=icon, l=label,
  )


# ═══════════════════════════════════════════════════════════════════════════
# CUSTOM ADMIN SITE
# ═══════════════════════════════════════════════════════════════════════════

class RoastAdminSite(admin.AdminSite):
  site_header = ' Scorify'
  site_title = 'Scorify Admin'
  index_title = 'Control Panel'

  def get_urls(self):
    custom = [
      path('dashboard/', self.admin_view(self.dashboard_view), name='scorify_dashboard'),
    ]
    return custom + super().get_urls()

  # ── Dashboard ────────────────────────────────────────────────────────
  def dashboard_view(self, request):
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week = now - timedelta(days=7)

    total_users = User.objects.count()
    total_analyses = CVAnalysis.objects.count()
    today_uploads = CVAnalysis.objects.filter(created_at__gte=today).count()
    week_uploads = CVAnalysis.objects.filter(created_at__gte=week).count()
    avg_score_val = (
      CVAnalysis.objects
      .filter(overall_score__isnull=False)
      .aggregate(a=Avg('overall_score'))['a'] or 0
    )
    free_users = UserProfile.objects.filter(plan='free').count()
    pro_users = UserProfile.objects.filter(plan='pro').count()
    vip_users = UserProfile.objects.filter(plan='vip').count()
    active_otps = OTPCode.objects.filter(
      is_used=False,
      created_at__gte=now - timedelta(minutes=10),
    ).count()

    recent_analyses = CVAnalysis.objects.select_related('user').order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-date_joined')[:5]

    # Daily uploads for the past 7 days (chart data)
    daily = []
    for i in range(6, -1, -1):
      day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
      day_end = day_start + timedelta(days=1)
      count = CVAnalysis.objects.filter(
        created_at__gte=day_start,
        created_at__lt=day_end,
      ).count()
      daily.append({'label': day_start.strftime('%b %d'), 'count': count})

    ctx = {
      **self.each_context(request),
      'title': 'Dashboard',
      'total_users': total_users,
      'total_analyses': total_analyses,
      'today_uploads': today_uploads,
      'week_uploads': week_uploads,
      'avg_score': round(avg_score_val, 1),
      'free_users': free_users,
      'pro_users': pro_users,
      'vip_users': vip_users,
      'recent_analyses': recent_analyses,
      'recent_users': recent_users,
      'active_otps': active_otps,
      'daily_json': json.dumps(daily),
    }
    return render(request, 'admin/scorify_dashboard.html', ctx)

  # ── Index: inject quick stats ────────────────────────────────────────
  def index(self, request, extra_context=None):
    extra_context = extra_context or {}
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    extra_context.update({
      'total_users': User.objects.count(),
      'total_analyses': CVAnalysis.objects.count(),
      'today_uploads': CVAnalysis.objects.filter(created_at__gte=today).count(),
      'pro_users': UserProfile.objects.filter(plan__in=['pro', 'vip']).count(),
    })
    return super().index(request, extra_context)


admin_site = RoastAdminSite(name='admin')


# ═══════════════════════════════════════════════════════════════════════════
# USERPROFILE ADMIN
# ═══════════════════════════════════════════════════════════════════════════

@admin.register(UserProfile, site=admin_site)
class UserProfileAdmin(admin.ModelAdmin):
  list_display = ['user_info', 'plan_col', 'total_uploads', 'best_score_col', 'completion_col', 'joined']
  list_filter = ['plan', 'public_profile', 'created_at']
  search_fields = ['user__username', 'user__email', 'job_title', 'industry']
  readonly_fields = ['created_at', 'badges_display', 'score_trend_display', 'uploads_today_display']
  ordering = ['-created_at']
  actions = ['make_pro', 'make_vip', 'make_free', 'export_csv']
  list_per_page = 25

  fieldsets = (
    ('User', {'fields': ('user', 'plan', 'avatar')}),
    ('Profile Info', {'fields': ('job_title', 'industry', 'bio', 'career_goal', 'skills_tags')}),
    ('Settings', {'fields': ('public_profile', 'onboarding_done')}),
    ('Stats (read-only)', {
      'fields': ('total_uploads', 'best_score', 'uploads_today_display',
            'score_trend_display', 'badges_display', 'created_at'),
    }),
    ('Pro Settings', {'fields': ('pro_since', 'pro_expires'), 'classes': ('collapse',)}),
  )

  class Media:
    css = {'all': ('roaster/css/admin.css',)}
    js = ('roaster/js/admin.js',)

  # ── List columns ─────────────────────────────────────────────────────

  def user_info(self, obj):
    if obj.avatar:
      avatar_html = (
        f'<img src="{obj.avatar.url}" style="width:34px;height:34px;border-radius:50%;'
        f'object-fit:cover;margin-right:10px;border:2px solid rgba(255,77,0,.4)">'
      )
    else:
      letter = (obj.user.username[0] if obj.user.username else '?').upper()
      avatar_html = (
        f'<span style="display:inline-flex;align-items:center;justify-content:center;'
        f'width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#ff4d00,#ffaa00);'
        f'color:#0a0804;font-weight:900;font-size:.85rem;margin-right:10px">{letter}</span>'
      )
    return format_html(
      '<div style="display:flex;align-items:center">{}<div>'
      '<div style="font-weight:700;color:#fff8ee">{}</div>'
      '<div style="font-size:.75rem;color:#8a7a6a">{}</div>'
      '</div></div>',
      avatar_html, obj.user.username, obj.user.email,
    )
  user_info.short_description = 'User'
  user_info.admin_order_field = 'user__username'

  def plan_col(self, obj):
    return plan_badge(obj.plan)
  plan_col.short_description = 'Plan'
  plan_col.admin_order_field = 'plan'

  def best_score_col(self, obj):
    return score_badge(obj.best_score if obj.best_score > 0 else None)
  best_score_col.short_description = 'Best Score'

  def completion_col(self, obj):
    pct = obj.profile_completion
    color = '#4ade80' if pct >= 80 else ('#ffaa00' if pct >= 40 else '#f87171')
    return format_html(
      '<div style="display:flex;align-items:center;gap:8px;min-width:100px">'
      '<div style="flex:1;height:6px;background:rgba(255,255,255,.08);border-radius:3px;overflow:hidden">'
      '<div style="width:{p}%;height:100%;background:{c}"></div></div>'
      '<span style="font-size:.75rem;color:{c};font-weight:700;font-family:monospace">{p}%</span>'
      '</div>',
      p=pct, c=color,
    )
  completion_col.short_description = 'Profile'

  def joined(self, obj):
    return format_html(
      '<span style="color:#8a7a6a;font-size:.78rem;font-family:monospace">{}</span>',
      obj.created_at.strftime('%b %d, %Y'),
    )
  joined.short_description = 'Joined'
  joined.admin_order_field = 'created_at'

  # ── Detail-only read-only fields ─────────────────────────────────────

  def uploads_today_display(self, obj):
    return format_html('<strong>{}</strong> uploads today', obj.uploads_today)
  uploads_today_display.short_description = 'Today'

  def score_trend_display(self, obj):
    trend = obj.score_trend
    icon = {'up': '📈', 'down': '📉', 'neutral': '➡️'}.get(trend, '➡️')
    return format_html('{} {}', icon, trend.upper())
  score_trend_display.short_description = 'Score Trend'

  def badges_display(self, obj):
    badges = obj.achievements
    if not badges:
      return 'No achievements yet'
    return format_html(' '.join(f'{b["icon"]} {b["name"]}' for b in badges))
  badges_display.short_description = 'Achievements'

  # ── Actions ──────────────────────────────────────────────────────────

  def make_pro(self, request, qs):
    n = qs.update(plan='pro')
    self.message_user(request, f'✅ {n} user(s) upgraded to Pro.')
  make_pro.short_description = '🔵 Upgrade selected to Pro'

  def make_vip(self, request, qs):
    n = qs.update(plan='vip')
    self.message_user(request, f' {n} user(s) upgraded to VIP.')
  make_vip.short_description = ' Upgrade selected to VIP'

  def make_free(self, request, qs):
    n = qs.update(plan='free')
    self.message_user(request, f'⚪ {n} user(s) downgraded to Free.')
  make_free.short_description = '⚪ Downgrade selected to Free'

  def export_csv(self, request, qs):
    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    writer = csv.writer(resp)
    writer.writerow(['Username', 'Email', 'Plan', 'Total Uploads', 'Best Score', 'Joined'])
    for p in qs.select_related('user'):
      writer.writerow([
        p.user.username,
        p.user.email,
        p.plan,
        p.total_uploads,
        p.best_score,
        p.created_at.strftime('%Y-%m-%d'),
      ])
    return resp
  export_csv.short_description = '📥 Export selected to CSV'


# ═══════════════════════════════════════════════════════════════════════════
# CVANALYSIS ADMIN
# ═══════════════════════════════════════════════════════════════════════════

@admin.register(CVAnalysis, site=admin_site)
class CVAnalysisAdmin(admin.ModelAdmin):
  list_display = ['filename_col', 'user_col', 'score_col', 'doc_type_col',
            'verdict_col', 'plan_col', 'time_col', 'date_col']
  list_filter = ['plan_used', 'is_preview', 'created_at']
  search_fields = ['user__username', 'user__email', 'original_filename', 'verdict']
  readonly_fields = ['id', 'created_at', 'processing_time', 'analysis_preview', 'ip_address']
  ordering = ['-created_at']
  date_hierarchy = 'created_at'
  list_per_page = 30
  actions = ['export_csv', 'delete_previews']

  fieldsets = (
    ('File Info', {'fields': ('user', 'original_filename', 'plan_used', 'is_preview')}),
    ('Scores', {'fields': ('overall_score', 'verdict')}),
    ('Meta', {'fields': ('id', 'ip_address', 'processing_time', 'created_at')}),
    ('Full Analysis (JSON)', {'fields': ('analysis_preview',), 'classes': ('collapse',)}),
  )

  class Media:
    css = {'all': ('roaster/css/admin.css',)}
    js = ('roaster/js/admin.js',)

  # ── List columns ─────────────────────────────────────────────────────

  def filename_col(self, obj):
    name = obj.original_filename
    short = (name[:30] + '…') if len(name) > 30 else name
    return format_html(
      '<span title="{}" style="font-family:monospace;font-size:.82rem;color:#c8b89a">{}</span>',
      name, short,
    )
  filename_col.short_description = 'File'
  filename_col.admin_order_field = 'original_filename'

  def user_col(self, obj):
    if obj.user:
      return format_html(
        '<a href="/admin/auth/user/{}/change/" style="color:#ffaa00;font-weight:600">{}</a>',
        obj.user.id, obj.user.username,
      )
    return format_html('<span style="color:#555;font-style:italic">Anonymous</span>')
  user_col.short_description = 'User'

  def score_col(self, obj):
    return score_badge(obj.overall_score)
  score_col.short_description = 'Score'
  score_col.admin_order_field = 'overall_score'

  def doc_type_col(self, obj):
    dt = (obj.analysis_data or {}).get('document_type', '')
    if dt:
      return format_html(
        '<span style="font-size:.72rem;color:#8a7a6a;font-family:monospace">{}</span>',
        dt[:20],
      )
    return format_html('<span style="color:#444">CV</span>')
  doc_type_col.short_description = 'Type'

  def verdict_col(self, obj):
    if not obj.verdict:
      return '—'
    s = obj.overall_score or 0
    fg = '#f87171' if s < 40 else ('#ffaa00' if s < 65 else '#4ade80')
    bg = ('rgba(248,113,113,.1)' if s < 40 else
       ('rgba(255,170,0,.1)' if s < 65 else 'rgba(74,222,128,.1)'))
    return format_html(
      '<span style="background:{bg};color:{fg};padding:2px 10px;border-radius:99px;'
      'font-size:.72rem;font-weight:700;font-family:monospace">{v}</span>',
      bg=bg, fg=fg, v=obj.verdict[:20],
    )
  verdict_col.short_description = 'Verdict'

  def plan_col(self, obj):
    return plan_badge(obj.plan_used)
  plan_col.short_description = 'Plan'

  def time_col(self, obj):
    if obj.processing_time:
      return format_html(
        '<span style="font-family:monospace;color:#8a7a6a;font-size:.78rem">{}s</span>',
        obj.processing_time,
      )
    return '—'
  time_col.short_description = '⏱'

  def date_col(self, obj):
    return format_html(
      '<span style="color:#8a7a6a;font-size:.78rem;font-family:monospace">{}</span>',
      obj.created_at.strftime('%b %d, %H:%M'),
    )
  date_col.short_description = 'Date'
  date_col.admin_order_field = 'created_at'

  # ── Detail-only ───────────────────────────────────────────────────────

  def analysis_preview(self, obj):
    if not obj.analysis_data:
      return 'No data'
    formatted = json.dumps(obj.analysis_data, indent=2, ensure_ascii=False)
    return format_html(
      '<pre style="background:#0a0804;color:#4ade80;padding:16px;border-radius:10px;'
      'font-size:.75rem;max-height:400px;overflow:auto;border:1px solid rgba(74,222,128,.2)">{}</pre>',
      formatted,
    )
  analysis_preview.short_description = 'Analysis JSON'

  # ── Actions ──────────────────────────────────────────────────────────

  def export_csv(self, request, qs):
    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename="analyses_export.csv"'
    writer = csv.writer(resp)
    writer.writerow(['ID', 'User', 'File', 'Score', 'Verdict', 'Plan', 'Document Type', 'Date'])
    for a in qs.select_related('user'):
      doc_type = (a.analysis_data or {}).get('document_type', 'CV')
      writer.writerow([
        str(a.id),
        a.user.username if a.user else 'Anonymous',
        a.original_filename,
        a.overall_score,
        a.verdict,
        a.plan_used,
        doc_type,
        a.created_at.strftime('%Y-%m-%d %H:%M'),
      ])
    return resp
  export_csv.short_description = '📥 Export selected to CSV'

  def delete_previews(self, request, qs):
    deleted, _ = qs.filter(is_preview=True).delete()
    self.message_user(request, f'🗑 Deleted {deleted} preview analysis record(s).')
  delete_previews.short_description = '🗑 Delete preview analyses'


# ═══════════════════════════════════════════════════════════════════════════
# OTP ADMIN
# ═══════════════════════════════════════════════════════════════════════════

@admin.register(OTPCode, site=admin_site)
class OTPCodeAdmin(admin.ModelAdmin):
  list_display = ['email_col', 'code_col', 'status_col', 'expires_col', 'created_col']
  list_filter = ['is_used', 'created_at']
  search_fields = ['email']
  readonly_fields = ['created_at']
  ordering = ['-created_at']
  list_per_page = 50
  actions = ['delete_expired', 'delete_used']

  class Media:
    css = {'all': ('roaster/css/admin.css',)}
    js = ('roaster/js/admin.js',)

  def email_col(self, obj):
    return format_html(
      '<span style="color:#c8b89a;font-family:monospace">{}</span>', obj.email
    )
  email_col.short_description = 'Email'

  def code_col(self, obj):
    return format_html(
      '<span style="font-family:monospace;font-size:1.1rem;font-weight:800;'
      'color:#ffaa00;letter-spacing:.3em">{}</span>',
      obj.code,
    )
  code_col.short_description = 'Code'

  def status_col(self, obj):
    if obj.is_used:
      return format_html(
        '<span style="background:rgba(100,116,139,.2);color:#94a3b8;'
        'padding:2px 10px;border-radius:99px;font-size:.72rem">USED</span>'
      )
    if obj.is_valid():
      return format_html(
        '<span style="background:rgba(74,222,128,.15);color:#4ade80;'
        'padding:2px 10px;border-radius:99px;font-size:.72rem;font-weight:700">✓ ACTIVE</span>'
      )
    return format_html(
      '<span style="background:rgba(248,113,113,.15);color:#f87171;'
      'padding:2px 10px;border-radius:99px;font-size:.72rem">EXPIRED</span>'
    )
  status_col.short_description = 'Status'

  def expires_col(self, obj):
    if obj.is_used or not obj.is_valid():
      return '—'
    expires = obj.created_at + timedelta(minutes=10)
    remaining = max(0, int((expires - timezone.now()).total_seconds() // 60))
    return format_html(
      '<span style="color:#ffaa00;font-size:.78rem;font-family:monospace">{}m left</span>',
      remaining,
    )
  expires_col.short_description = 'Expires'

  def created_col(self, obj):
    return format_html(
      '<span style="color:#8a7a6a;font-size:.78rem;font-family:monospace">{}</span>',
      obj.created_at.strftime('%b %d, %H:%M:%S'),
    )
  created_col.short_description = 'Created'

  # ── Actions ──────────────────────────────────────────────────────────

  def delete_expired(self, request, qs):
    cutoff = timezone.now() - timedelta(minutes=10)
    deleted, _ = OTPCode.objects.filter(created_at__lt=cutoff, is_used=False).delete()
    self.message_user(request, f'🗑 Deleted {deleted} expired OTP code(s).')
  delete_expired.short_description = '🗑 Delete all expired OTPs (site-wide)'

  def delete_used(self, request, qs):
    deleted, _ = OTPCode.objects.filter(is_used=True).delete()
    self.message_user(request, f'🗑 Deleted {deleted} used OTP code(s).')
  delete_used.short_description = '🗑 Delete all used OTPs (site-wide)'


# ═══════════════════════════════════════════════════════════════════════════
# USER ADMIN (Django built-in User model, extended with plan inline)
# ═══════════════════════════════════════════════════════════════════════════

@admin.register(User, site=admin_site)
class UserAdmin(BaseUserAdmin):
  list_display = ['username_col', 'email', 'plan_inline', 'is_staff', 'date_joined']
  list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
  search_fields = ['username', 'email', 'first_name', 'last_name']
  ordering = ['-date_joined']

  class Media:
    css = {'all': ('roaster/css/admin.css',)}
    js = ('roaster/js/admin.js',)

  def username_col(self, obj):
    return format_html('<strong style="color:#fff8ee">{}</strong>', obj.username)
  username_col.short_description = 'Username'
  username_col.admin_order_field = 'username'

  def plan_inline(self, obj):
    try:
      return plan_badge(obj.profile.plan)
    except UserProfile.DoesNotExist:
      return format_html('<span style="color:#555">—</span>')
  plan_inline.short_description = 'Plan'


# ── New model registrations ───────────────────────────────────────────────
from .models import CVCache, RateLimitRecord, ReferralCode, ReferralUse, ShareCard, BlogPost

@admin.register(CVCache, site=admin_site)
class CVCacheAdmin(admin.ModelAdmin):
  list_display = ['cv_hash_short', 'plan', 'hit_count', 'created_at']
  list_filter = ['plan', 'created_at']
  ordering = ['-created_at']
  actions = ['clear_cache']
  class Media:
    css = {'all': ('roaster/css/admin.css',)}

  def cv_hash_short(self, obj):
    return format_html('<span style="font-family:monospace;font-size:.78rem">{}</span>', obj.cv_hash[:16] + '…')
  cv_hash_short.short_description = 'CV Hash'

  def clear_cache(self, request, qs):
    n, _ = qs.delete()
    self.message_user(request, f'🗑 Cleared {n} cache entries')
  clear_cache.short_description = '🗑 Clear selected cache entries'


@admin.register(RateLimitRecord, site=admin_site)
class RateLimitRecordAdmin(admin.ModelAdmin):
  list_display = ['ip', 'created_at']
  list_filter = ['created_at']
  ordering = ['-created_at']
  actions = ['cleanup_old']
  class Media:
    css = {'all': ('roaster/css/admin.css',)}

  def cleanup_old(self, request, qs):
    RateLimitRecord.cleanup()
    self.message_user(request, '🗑 Old rate limit records cleaned up')
  cleanup_old.short_description = '🗑 Cleanup records older than 2 hours'


@admin.register(ReferralCode, site=admin_site)
class ReferralCodeAdmin(admin.ModelAdmin):
  list_display = ['user_col', 'code', 'total_referrals', 'bonus_uploads_earned', 'created_at']
  search_fields = ['user__username', 'code']
  ordering = ['-total_referrals']
  class Media:
    css = {'all': ('roaster/css/admin.css',)}

  def user_col(self, obj):
    return format_html('<strong style="color:#fff8ee">{}</strong>', obj.user.username)
  user_col.short_description = 'User'


@admin.register(ShareCard, site=admin_site)
class ShareCardAdmin(admin.ModelAdmin):
  list_display = ['id_short', 'analysis_col', 'is_public', 'view_count', 'created_at']
  list_filter = ['is_public', 'created_at']
  ordering = ['-created_at']
  class Media:
    css = {'all': ('roaster/css/admin.css',)}

  def id_short(self, obj):
    return format_html('<span style="font-family:monospace;font-size:.78rem">{}</span>', str(obj.id)[:8] + '…')
  id_short.short_description = 'ID'

  def analysis_col(self, obj):
    return format_html('<span style="font-size:.8rem">{}/100 — {}</span>', obj.analysis.overall_score, obj.analysis.original_filename[:30])
  analysis_col.short_description = 'Analysis'


@admin.register(BlogPost, site=admin_site)
class BlogPostAdmin(admin.ModelAdmin):
  list_display = ['title', 'published', 'view_count', 'read_time_col', 'created_at']
  list_filter = ['published', 'created_at']
  search_fields = ['title', 'content', 'tags']
  ordering = ['-created_at']
  prepopulated_fields = {'slug': ('title',)}
  class Media:
    css = {'all': ('roaster/css/admin.css',)}

  def read_time_col(self, obj):
    return f'{obj.read_time} min'
  read_time_col.short_description = 'Read time'