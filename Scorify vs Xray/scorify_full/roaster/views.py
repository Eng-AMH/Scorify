"""
Scorify — Views
All correctness guarantees:
- profile = None always initialized before use
- Temp file always deleted in finally block
- Plan checks before every Pro/VIP feature
"""
import json
import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db.models import Avg, Count, Max, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .ai import analyze_cv, build_cv, compare_cvs, optimize_ats
from .emails import send_otp_email, send_pro_email, send_welcome_email, send_weekly_digest
from .models import (BlogPost, CVAnalysis, CVCache, OTPCode, RateLimitRecord,
           ReferralCode, ReferralUse, ShareCard, UserProfile)
from .utils import extract_text_from_file, is_valid_cv_file


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _ip(request):
  xff = request.META.get('HTTP_X_FORWARDED_FOR')
  return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '0.0.0.0')

def _preview(full):
  return {
    'overall_score': full.get('overall_score'),
    'verdict': full.get('verdict'),
    'summary': full.get('summary'),
    'roast_lines': full.get('roast_lines', [])[:2],
    'estimated_interview_chance': full.get('estimated_interview_chance'),
    'document_type': full.get('document_type', 'Document'),
    'is_preview': True,
  }

def _ensure_profile(user):
  profile, _ = UserProfile.objects.get_or_create(user=user)
  return profile

def _unique_username(base):
  base = base[:28]
  username = base
  n = 1
  while User.objects.filter(username=username).exists():
    username = f'{base[:25]}{n}'; n += 1
  return username

def _json_body(request):
  """Parse JSON safely and return {} for empty/invalid bodies."""
  try:
    raw = request.body.decode('utf-8') if hasattr(request.body, 'decode') else request.body
    if not raw:
      return {}
    return json.loads(raw)
  except (TypeError, ValueError, UnicodeDecodeError):
    return {}


def _first_user_by_email(email):
  return User.objects.filter(email__iexact=email).order_by('-id').first()


def _first_user_by_identity(identity):
  return User.objects.filter(
    Q(username__iexact=identity) | Q(email__iexact=identity)
  ).order_by('-id').first()


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC PAGES
# ═══════════════════════════════════════════════════════════════════════════

@ensure_csrf_cookie

def index(request):
  return render(request, 'roaster/index.html')

def logout_view(request):
  logout(request)
  return redirect('index')

def public_profile(request, username):
  user = get_object_or_404(User, username=username)
  profile = _ensure_profile(user)
  if not profile.public_profile:
    return render(request, 'roaster/profile_private.html', {'username': username})
  analyses = CVAnalysis.objects.filter(user=user, is_preview=False).order_by('-created_at')[:5]
  return render(request, 'roaster/public_profile.html', {'profile': profile, 'analyses': analyses})


# ═══════════════════════════════════════════════════════════════════════════
# AUTH PAGES
# ═══════════════════════════════════════════════════════════════════════════

@ensure_csrf_cookie

def login_view(request):
  if request.user.is_authenticated: return redirect('dashboard')
  return render(request, 'roaster/login.html')

@ensure_csrf_cookie

def register_view(request):
  if request.user.is_authenticated: return redirect('dashboard')
  return render(request, 'roaster/register.html')

@ensure_csrf_cookie

def forgot_password_view(request):
  if request.user.is_authenticated: return redirect('dashboard')
  return render(request, 'roaster/forgot_password.html')


# ═══════════════════════════════════════════════════════════════════════════
# AUTH APIs
# ═══════════════════════════════════════════════════════════════════════════

@require_http_methods(['POST'])
def login_submit(request):
  try:
    data = _json_body(request)
    identity = data.get('identity', '').strip()
    password = data.get('password', '').strip()
    if not identity or not password:
      return JsonResponse({'error': 'Please enter your email/username and password.'}, status=400)
    user = None
    candidates = User.objects.filter(
      Q(username__iexact=identity) | Q(email__iexact=identity)
    ).order_by('-id')
    for candidate in candidates:
      authenticated = authenticate(request, username=candidate.username, password=password)
      if authenticated:
        user = authenticated
        break
    if not user:
      fallback = _first_user_by_identity(identity)
      if fallback and fallback.check_password(password):
        user = fallback
    if not user:
      return JsonResponse({'error': 'Incorrect email/username or password.'}, status=400)
    login(request, user)
    return JsonResponse({'success': True, 'redirect': '/dashboard/'})
  except Exception as e:
    return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['POST'])
def register_set_password(request):
  try:
    data = _json_body(request)
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    ref_code = data.get('referral_code', '').strip().upper()
    if not email or not password:
      return JsonResponse({'error': 'Email and password are required.'}, status=400)
    if len(password) < 6:
      return JsonResponse({'error': 'Password must be at least 6 characters.'}, status=400)
    verified = request.session.get('otp_verified_email', '')
    if verified != email:
      return JsonResponse({'error': 'Please verify your email first.'}, status=400)
    base = email.split('@')[0].replace('.','_').replace('-','_').replace('+','_')
    username = _unique_username(base)
    user = _first_user_by_email(email)
    created = user is None
    if created:
      user = User.objects.create(email=email, username=username)
    else:
      if not user.username:
        user.username = username
    user.set_password(password)
    user.save()
    if created:
      profile = _ensure_profile(user)
      send_welcome_email(user)
      # Apply referral code if provided
      if ref_code:
        try:
          ref = ReferralCode.objects.get(code=ref_code)
          if ref.user != user:
            ReferralUse.objects.get_or_create(referral_code=ref, referred_user=user)
            from django.conf import settings as django_settings
            bonus = getattr(django_settings, 'REFERRAL_BONUS_UPLOADS', 3)
            ref.total_referrals += 1
            ref.bonus_uploads_earned += bonus
            ref.save()
            ref.user.profile.bonus_uploads += bonus
            ref.user.profile.save()
            profile.bonus_uploads += bonus
            profile.save()
        except ReferralCode.DoesNotExist:
          pass
    request.session.pop('otp_verified_email', None)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return JsonResponse({'success': True, 'redirect': '/dashboard/'})
  except Exception as e:
    return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['POST'])
def reset_password_submit(request):
  try:
    data = _json_body(request)
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    if not email or not password:
      return JsonResponse({'error': 'Email and password are required.'}, status=400)
    if len(password) < 6:
      return JsonResponse({'error': 'Password must be at least 6 characters.'}, status=400)
    verified = request.session.get('otp_verified_email', '')
    if verified != email:
      return JsonResponse({'error': 'Please verify your email first.'}, status=400)
    user = _first_user_by_email(email)
    if not user:
      return JsonResponse({'error': 'No account found with this email.'}, status=400)
    user.set_password(password)
    user.save()
    request.session.pop('otp_verified_email', None)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return JsonResponse({'success': True, 'redirect': '/dashboard/'})
  except Exception as e:
    return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['POST'])
def send_otp(request):
  try:
    data = _json_body(request)
    email = data.get('email', '').strip().lower()
    if not email or '@' not in email or '.' not in email:
      return JsonResponse({'error': 'Please enter a valid email address.'}, status=400)
    code = OTPCode.generate_code()
    pending_id = data.get('pending_analysis_id') or None
    OTPCode.objects.create(email=email, code=code, pending_analysis_id=pending_id)
    send_otp_email(email, code)
    return JsonResponse({'success': True, 'message': f'Code sent to {email}'})
  except Exception as e:
    return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['POST'])
def verify_otp(request):
  try:
    data = _json_body(request)
    email = data.get('email', '').strip().lower()
    code = data.get('code', '').strip()
    mode = data.get('mode', 'index')
    if not email or not code:
      return JsonResponse({'error': 'Email and code are required.'}, status=400)
    otp = OTPCode.objects.filter(email=email, code=code, is_used=False).order_by('-created_at').first()
    if not otp:
      return JsonResponse({'error': 'Invalid code. Please try again.'}, status=400)
    if not otp.is_valid():
      return JsonResponse({'error': 'Code expired. Please request a new one.'}, status=400)
    otp.is_used = True
    otp.save()
    if mode in ('register', 'forgot'):
      request.session['otp_verified_email'] = email
      return JsonResponse({'success': True, 'next': 'set_password'})
    base = email.split('@')[0].replace('.','_').replace('-','_').replace('+','_')
    user = _first_user_by_email(email)
    created = user is None
    if created:
      user = User.objects.create(email=email, username=_unique_username(base))
      user.set_unusable_password()
      user.save()
      _ensure_profile(user)
      send_welcome_email(user)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    profile = _ensure_profile(user)
    if otp.pending_analysis_id:
      try:
        cv = CVAnalysis.objects.get(id=otp.pending_analysis_id)
        cv.user = user; cv.is_preview = False; cv.plan_used = profile.plan; cv.save()
        profile.total_uploads += 1
        score = cv.overall_score or 0
        if score > profile.best_score: profile.best_score = score
        profile.save()
        return JsonResponse({'success':True,'redirect':'/dashboard/',
          'analysis_id':str(cv.id),'analysis':cv.analysis_data,'is_new_user':created})
      except CVAnalysis.DoesNotExist:
        pass
    return JsonResponse({'success': True, 'redirect': '/dashboard/', 'is_new_user': created})
  except Exception as e:
    return JsonResponse({'error': str(e)}, status=500)


# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

@login_required
@ensure_csrf_cookie
def dashboard(request):
  profile = _ensure_profile(request.user)
  analyses = CVAnalysis.objects.filter(user=request.user).order_by('-created_at')[:20]
  score_history = list(
    CVAnalysis.objects.filter(user=request.user, overall_score__isnull=False)
    .order_by('created_at').values('overall_score', 'created_at')[:10])
  show_onboarding = not profile.onboarding_done
  ref_code = ReferralCode.get_or_create_for_user(request.user)
  return render(request, 'roaster/dashboard.html', {
    'profile': profile,
    'analyses': analyses,
    'score_history': json.dumps([
      {'score': s['overall_score'], 'date': s['created_at'].strftime('%b %d')}
      for s in score_history]),
    'uploads_today': profile.uploads_today,
    'uploads_remaining':profile.uploads_remaining_today,
    'show_onboarding': show_onboarding,
    'ref_code': ref_code,
  })


@login_required
def profile_view(request):
  profile = _ensure_profile(request.user)
  if request.method == 'POST':
    request.user.first_name = request.POST.get('first_name','')[:50]
    request.user.last_name = request.POST.get('last_name','')[:50]
    request.user.save()
    profile.job_title = request.POST.get('job_title','')[:100]
    profile.industry = request.POST.get('industry','')[:100]
    profile.bio = request.POST.get('bio','')[:300]
    profile.career_goal = request.POST.get('career_goal','')[:200]
    profile.skills_tags = request.POST.get('skills_tags','')
    profile.public_profile = request.POST.get('public_profile') == 'on'
    if 'avatar' in request.FILES:
      av = request.FILES['avatar']
      if av.size <= 2 * 1024 * 1024:
        profile.avatar = av
    profile.save()
    return JsonResponse({'success': True, 'message': 'Profile updated!'})
  all_analyses = CVAnalysis.objects.filter(user=request.user).order_by('-created_at')
  return render(request, 'roaster/profile.html', {'profile': profile, 'analyses': all_analyses})


@login_required
@require_http_methods(['POST'])
def change_password_view(request):
  try:
    data = _json_body(request)
    old = data.get('old_password','')
    new = data.get('new_password','')
    if not request.user.check_password(old):
      return JsonResponse({'error': 'Current password is incorrect.'}, status=400)
    if len(new) < 6:
      return JsonResponse({'error': 'New password must be at least 6 characters.'}, status=400)
    request.user.set_password(new)
    request.user.save()
    update_session_auth_hash(request, request.user)
    return JsonResponse({'success': True, 'message': 'Password changed!'})
  except Exception as e:
    return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(['POST'])
def onboarding_done(request):
  profile = _ensure_profile(request.user)
  profile.onboarding_done = True
  profile.save(update_fields=['onboarding_done'])
  return JsonResponse({'success': True})


# ═══════════════════════════════════════════════════════════════════════════
# CV UPLOAD (profile=None always initialized; finally always cleans up)
# ═══════════════════════════════════════════════════════════════════════════

@require_http_methods(['POST'])
def upload_cv(request):
  profile = None
  if request.user.is_authenticated:
    profile = _ensure_profile(request.user)
    if not profile.can_upload:
      return JsonResponse({
        'error': 'upgrade_required',
        'message': 'Free plan: 3 analyses/day. Upgrade to Pro for unlimited! ',
        'plan': profile.plan,
      }, status=403)

  if 'cv_file' not in request.FILES:
    return JsonResponse({'error': 'No file uploaded.'}, status=400)

  cv_file = request.FILES['cv_file']
  job_desc = request.POST.get('job_description', '').strip()
  language = request.POST.get('language', '').strip() or None

  if not is_valid_cv_file(cv_file.name):
    return JsonResponse({'error': 'Please upload a PDF or Word document (.pdf, .doc, .docx).'}, status=400)
  if cv_file.size > 5 * 1024 * 1024:
    return JsonResponse({'error': 'File too large. Maximum 5MB allowed.'}, status=400)

  safe_name = cv_file.name.replace(' ', '_')
  file_path = default_storage.save(f'cvs/temp_{safe_name}', cv_file)
  full_path = default_storage.path(file_path)

  try:
    cv_text = extract_text_from_file(full_path)
    if len(cv_text.strip()) < 10:
      return JsonResponse({'error': 'Could not extract text. File may be a scanned image or empty.'}, status=400)

    is_auth = request.user.is_authenticated
    plan = profile.plan if (is_auth and profile is not None) else 'free'

    # Check cache first — avoid re-calling Groq for identical CVs
    cached = CVCache.lookup(cv_text, plan, job_desc)
    if cached:
      analysis = cached
      analysis['from_cache'] = True
    else:
      analysis = analyze_cv(cv_text, job_desc or None, plan=plan, language=language)
      CVCache.store(cv_text, plan, job_desc, analysis)

    cv_obj = CVAnalysis.objects.create(
      user = request.user if is_auth else None,
      session_key = request.session.session_key if not is_auth else None,
      original_filename = cv_file.name,
      overall_score = analysis.get('overall_score'),
      verdict = analysis.get('verdict', ''),
      analysis_data = analysis,
      is_preview = not is_auth,
      plan_used = plan,
      ip_address = _ip(request),
      processing_time = analysis.get('processing_time'),
    )

    if is_auth and profile is not None:
      # Consume bonus upload first if available
      if profile.bonus_uploads > 0:
        profile.bonus_uploads = max(0, profile.bonus_uploads - 1)
      profile.total_uploads += 1
      score = analysis.get('overall_score') or 0
      if score > profile.best_score:
        profile.best_score = score
      profile.save()
      return JsonResponse({
        'success': True,
        'analysis_id': str(cv_obj.id),
        'analysis': analysis,
        'is_preview': False,
        'filename': cv_file.name,
        'uploads_remaining': profile.uploads_remaining_today,
      })

    return JsonResponse({
      'success': True,
      'analysis_id': str(cv_obj.id),
      'analysis': _preview(analysis),
      'is_preview': True,
      'filename': cv_file.name,
    })

  except ValueError as e:
    return JsonResponse({'error': str(e)}, status=400)
  except Exception as e:
    return JsonResponse({'error': f'Something went wrong: {e}'}, status=500)
  finally:
    try:
      if os.path.exists(full_path):
        os.remove(full_path)
    except Exception:
      pass


def get_analysis(request, analysis_id):
  try:
    cv = CVAnalysis.objects.get(id=analysis_id)
    if request.user.is_authenticated and cv.user == request.user:
      return JsonResponse({'success':True,'analysis':cv.analysis_data,'is_preview':False,'filename':cv.original_filename})
    if cv.is_preview:
      return JsonResponse({'success':True,'analysis':_preview(cv.analysis_data),'is_preview':True})
    return JsonResponse({'error': 'Unauthorized'}, status=403)
  except CVAnalysis.DoesNotExist:
    return JsonResponse({'error': 'Analysis not found.'}, status=404)


def stats_view(request):
  data = CVAnalysis.objects.aggregate(total=Count('id'), avg=Avg('overall_score'))
  return JsonResponse({'total_roasted': data['total'] or 0, 'average_score': round(data['avg'] or 0)})


# ═══════════════════════════════════════════════════════════════════════════
# CV COMPARISON
# ═══════════════════════════════════════════════════════════════════════════

@login_required
@ensure_csrf_cookie
def compare_view(request):
  profile = _ensure_profile(request.user)
  if not profile.is_pro:
    messages.error(request, 'CV Comparison is a Pro feature. Upgrade to unlock it!')
    return redirect('upgrade')
  analyses = CVAnalysis.objects.filter(user=request.user, overall_score__isnull=False).order_by('-created_at')[:30]
  return render(request, 'roaster/compare.html', {'profile': profile, 'analyses': analyses})


@login_required
@require_http_methods(['POST'])
def compare_submit(request):
  profile = _ensure_profile(request.user)
  if not profile.is_pro:
    return JsonResponse({'error': 'Pro feature. Please upgrade.'}, status=403)
  try:
    data = _json_body(request)
    id_a = data.get('analysis_id_a')
    id_b = data.get('analysis_id_b')
    if not id_a or not id_b:
      return JsonResponse({'error': 'Please select two analyses.'}, status=400)
    if id_a == id_b:
      return JsonResponse({'error': 'Please select two different analyses.'}, status=400)
    cv_a = CVAnalysis.objects.get(id=id_a, user=request.user)
    cv_b = CVAnalysis.objects.get(id=id_b, user=request.user)
    def _text(cv_obj):
      d = cv_obj.analysis_data or {}
      return (f'[{cv_obj.original_filename}]\n'
          + '\n'.join(p for p in [d.get('summary',''),
            ' '.join(d.get('top_fixes',[])),
            ' '.join(l.get('text','') for l in d.get('roast_lines',[]))] if p))
    result = compare_cvs(_text(cv_a), _text(cv_b), cv_a.original_filename, cv_b.original_filename)
    result['stored_score_a'] = cv_a.overall_score
    result['stored_score_b'] = cv_b.overall_score
    result['date_a'] = cv_a.created_at.strftime('%b %d, %Y')
    result['date_b'] = cv_b.created_at.strftime('%b %d, %Y')
    return JsonResponse({'success': True, 'comparison': result})
  except CVAnalysis.DoesNotExist:
    return JsonResponse({'error': 'One or both analyses not found.'}, status=404)
  except ValueError as e:
    return JsonResponse({'error': str(e)}, status=400)
  except Exception as e:
    return JsonResponse({'error': f'Comparison failed: {e}'}, status=500)


# ═══════════════════════════════════════════════════════════════════════════
# ATS OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════════

@login_required
@ensure_csrf_cookie
def ats_optimizer_view(request):
  profile = _ensure_profile(request.user)
  if not profile.is_pro:
    messages.error(request, 'ATS Optimizer is a Pro feature. Upgrade to unlock it!')
    return redirect('upgrade')
  return render(request, 'roaster/ats_optimizer.html', {'profile': profile})


@login_required
@require_http_methods(['POST'])
def ats_optimizer_submit(request):
  profile = _ensure_profile(request.user)
  if not profile.is_pro:
    return JsonResponse({'error': 'Pro feature. Please upgrade.'}, status=403)

  if 'cv_file' not in request.FILES:
    return JsonResponse({'error': 'No CV file uploaded.'}, status=400)

  job_desc = request.POST.get('job_description', '').strip()
  language = request.POST.get('language', '').strip() or None

  if not job_desc:
    return JsonResponse({'error': 'Job description is required for ATS optimization.'}, status=400)

  cv_file = request.FILES['cv_file']
  safe_name = cv_file.name.replace(' ', '_')
  file_path = default_storage.save(f'cvs/ats_temp_{safe_name}', cv_file)
  full_path = default_storage.path(file_path)

  try:
    cv_text = extract_text_from_file(full_path)
    if len(cv_text.strip()) < 10:
      return JsonResponse({'error': 'Could not extract text from this file.'}, status=400)
    result = optimize_ats(cv_text, job_desc, language=language)
    return JsonResponse({'success': True, 'result': result})
  except ValueError as e:
    return JsonResponse({'error': str(e)}, status=400)
  except Exception as e:
    return JsonResponse({'error': f'Optimization failed: {e}'}, status=500)
  finally:
    try:
      if os.path.exists(full_path):
        os.remove(full_path)
    except Exception:
      pass


# ═══════════════════════════════════════════════════════════════════════════
# CV BUILDER
# ═══════════════════════════════════════════════════════════════════════════

@login_required
@ensure_csrf_cookie
def cv_builder_view(request):
  profile = _ensure_profile(request.user)
  if not profile.is_pro:
    messages.error(request, 'CV Builder is a Pro feature. Upgrade to unlock it!')
    return redirect('upgrade')
  return render(request, 'roaster/cv_builder.html', {'profile': profile})


@login_required
@require_http_methods(['POST'])
def cv_builder_submit(request):
  profile = _ensure_profile(request.user)
  if not profile.is_pro:
    return JsonResponse({'error': 'Pro feature. Please upgrade.'}, status=403)
  try:
    data = _json_body(request)
    language = data.pop('language', None)
    if not data.get('name') or not data.get('title'):
      return JsonResponse({'error': 'Name and target title are required.'}, status=400)
    result = build_cv(data, language=language)
    return JsonResponse({'success': True, 'cv': result})
  except ValueError as e:
    return JsonResponse({'error': str(e)}, status=400)
  except Exception as e:
    return JsonResponse({'error': f'CV builder failed: {e}'}, status=500)


# ═══════════════════════════════════════════════════════════════════════════
# LEADERBOARD
# ═══════════════════════════════════════════════════════════════════════════

@ensure_csrf_cookie

def leaderboard_view(request):
  top = (CVAnalysis.objects
      .filter(is_preview=False, overall_score__isnull=False, user__isnull=False)
      .select_related('user__profile')
      .order_by('-overall_score')[:50])
  entries = []
  for cv in top:
    profile = cv.user.profile
    entries.append({
      'username': cv.user.username if profile.public_profile else f'user_{cv.user.id}',
      'score': cv.overall_score,
      'verdict': cv.verdict,
      'plan': cv.plan_used,
      'date': cv.created_at.strftime('%b %d, %Y'),
      'is_public': profile.public_profile,
    })
  stats = CVAnalysis.objects.filter(is_preview=False, overall_score__isnull=False).aggregate(
    total=Count('id'), avg=Avg('overall_score'), best=Max('overall_score'))
  return render(request, 'roaster/leaderboard.html', {
    'entries': entries, 'stats': stats,
    'profile': _ensure_profile(request.user) if request.user.is_authenticated else None,
  })


# ═══════════════════════════════════════════════════════════════════════════
# SHARE CARD
# ═══════════════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(['POST'])
def generate_share(request, analysis_id):
  try:
    cv = CVAnalysis.objects.get(id=analysis_id, user=request.user)
    card, _ = ShareCard.objects.get_or_create(analysis=cv)
    from django.conf import settings as django_settings
    share_url = f'{django_settings.SITE_URL}/share/{card.id}/'
    return JsonResponse({'success': True, 'share_url': share_url, 'card_id': str(card.id)})
  except CVAnalysis.DoesNotExist:
    return JsonResponse({'error': 'Analysis not found.'}, status=404)
  except Exception as e:
    return JsonResponse({'error': str(e)}, status=500)


@ensure_csrf_cookie


def share_view(request, card_id):
  card = get_object_or_404(ShareCard, id=card_id, is_public=True)
  card.view_count += 1
  card.save(update_fields=['view_count'])
  cv = card.analysis
  profile = _ensure_profile(cv.user) if cv.user else None
  return render(request, 'roaster/share.html', {'card': card, 'cv': cv, 'profile': profile})


# ═══════════════════════════════════════════════════════════════════════════
# REFERRAL
# ═══════════════════════════════════════════════════════════════════════════

@login_required
@ensure_csrf_cookie
def referral_view(request):
  profile = _ensure_profile(request.user)
  ref_code = ReferralCode.get_or_create_for_user(request.user)
  uses = ReferralUse.objects.filter(referral_code=ref_code).select_related('referred_user').order_by('-created_at')[:10]
  from django.conf import settings as django_settings
  return render(request, 'roaster/referral.html', {
    'profile': profile,
    'ref_code': ref_code,
    'uses': uses,
    'site_url': django_settings.SITE_URL,
    'bonus_per_ref': getattr(django_settings, 'REFERRAL_BONUS_UPLOADS', 3),
  })


# ═══════════════════════════════════════════════════════════════════════════
# BLOG
# ═══════════════════════════════════════════════════════════════════════════

@ensure_csrf_cookie

def blog_view(request):
  posts = BlogPost.objects.filter(published=True).order_by('-created_at')
  tag = request.GET.get('tag', '')
  if tag:
    posts = [p for p in posts if tag in p.tag_list]
  return render(request, 'roaster/blog.html', {
    'posts': posts,
    'tag': tag,
    'profile': _ensure_profile(request.user) if request.user.is_authenticated else None,
  })


@ensure_csrf_cookie


def blog_post_view(request, slug):
  post = get_object_or_404(BlogPost, slug=slug, published=True)
  post.view_count += 1
  post.save(update_fields=['view_count'])
  related = BlogPost.objects.filter(published=True).exclude(id=post.id).order_by('-created_at')[:3]
  return render(request, 'roaster/blog_post.html', {
    'post': post,
    'related': related,
    'profile': _ensure_profile(request.user) if request.user.is_authenticated else None,
  })


# ═══════════════════════════════════════════════════════════════════════════
# PDF EXPORT
# ═══════════════════════════════════════════════════════════════════════════

@login_required
def export_pdf(request, analysis_id):
  profile = _ensure_profile(request.user)
  if not profile.is_pro:
    return JsonResponse({'error': 'PDF export is a Pro feature. Please upgrade.'}, status=403)
  try:
    cv = CVAnalysis.objects.get(id=analysis_id, user=request.user)
  except CVAnalysis.DoesNotExist:
    return JsonResponse({'error': 'Analysis not found.'}, status=404)

  try:
    import io
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    FIRE = colors.HexColor('#ff4d00')
    AMBER = colors.HexColor('#ffaa00')
    GREEN = colors.HexColor('#4ade80')
    DARK = colors.HexColor('#1a1208')
    SMOKE = colors.HexColor('#8a7a6a')

    def H1(t): return Paragraph(t, ParagraphStyle('H1', fontSize=22, textColor=FIRE, spaceAfter=4, fontName='Helvetica-Bold', alignment=TA_CENTER))
    def H2(t): return Paragraph(t, ParagraphStyle('H2', fontSize=13, textColor=DARK, spaceBefore=12, spaceAfter=4, fontName='Helvetica-Bold'))
    def Body(t, color=None): return Paragraph(t, ParagraphStyle('Body', fontSize=10, spaceAfter=4, textColor=color or colors.HexColor('#2a1a0a'), fontName='Helvetica', leading=14))
    def Small(t): return Paragraph(t, ParagraphStyle('Sm', fontSize=8, textColor=SMOKE, spaceAfter=2, fontName='Helvetica'))

    d = cv.analysis_data or {}
    score = cv.overall_score or 0
    score_color = FIRE if score < 40 else (AMBER if score < 65 else GREEN)

    story = [H1(' Scorify — Analysis Report')]
    story.append(Small(f'File: {cv.original_filename} | Plan: {cv.plan_used.upper()} | Date: {cv.created_at.strftime("%B %d, %Y")}'))
    story.append(Spacer(1, .3*cm))
    story.append(HRFlowable(width='100%', thickness=1, color=FIRE))
    story.append(Spacer(1, .3*cm))

    tbl = Table([[
      Paragraph(f'<b>{score}/100</b>', ParagraphStyle('SC', fontSize=28, textColor=score_color, fontName='Helvetica-Bold', alignment=TA_CENTER)),
      Paragraph(f'<b>{d.get("verdict","N/A")}</b>', ParagraphStyle('V', fontSize=16, textColor=score_color, fontName='Helvetica-Bold', alignment=TA_CENTER)),
      Paragraph(f'Interview Chance<br/><b>{d.get("estimated_interview_chance","N/A")}</b>', ParagraphStyle('IC', fontSize=10, textColor=SMOKE, alignment=TA_CENTER)),
    ]], colWidths=[4*cm, 9*cm, 4*cm])
    tbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#fff8ee')),('BOX',(0,0),(-1,-1),1,FIRE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12)]))
    story += [tbl, Spacer(1,.4*cm)]

    if d.get('summary'):
      story += [H2('📝 Summary'), Body(d['summary'])]

    if d.get('sections'):
      story.append(H2('📊 Section Breakdown'))
      rows = [['Section','Score','Feedback']]
      for key, val in d['sections'].items():
        s = val.get('score',0); sc = '#4ade80' if s>=70 else ('#ffaa00' if s>=40 else '#f87171')
        rows.append([key.replace('_',' ').title(), Paragraph(f'<b>{s}/100</b>', ParagraphStyle('ts', fontSize=10, textColor=colors.HexColor(sc), fontName='Helvetica-Bold', alignment=TA_CENTER)), val.get('feedback','')])
      t = Table(rows, colWidths=[3.5*cm,2*cm,11.5*cm])
      t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),DARK),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#fffdf8'),colors.HexColor('#fff4e8')]),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#e8d8c0')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
      story += [t, Spacer(1,.3*cm)]

    if d.get('roast_lines'):
      story.append(H2(' Roast Lines'))
      for line in d['roast_lines']:
        t = line.get('type','amber'); ic = {'fire':'🔴','amber':'🟡','green':'🟢'}.get(t,'•'); c = {'fire':FIRE,'amber':AMBER,'green':GREEN}.get(t,SMOKE)
        story.append(Body(f'{ic} {line.get("text","")}', color=c))

    for section, title in [('top_fixes','🛠️ Top Fixes'),('strengths','💪 Strengths')]:
      if d.get(section):
        story.append(H2(title))
        for i, item in enumerate(d[section], 1):
          story.append(Body(f'<b>{i}.</b> {item}', color=GREEN if section=='strengths' else None))

    if d.get('ats_score') is not None:
      story.append(H2(f'🤖 ATS Score: {d["ats_score"]}/100'))
      for iss in d.get('ats_issues',[]): story.append(Body(f'⚠ {iss}', color=AMBER))

    if d.get('rewrite_suggestions'):
      story.append(H2('✏️ Rewrite Suggestions'))
      for rw in d['rewrite_suggestions']:
        story += [Body(f'<b>Before:</b> {rw.get("original","")}'), Body(f'<b>After:</b> {rw.get("improved","")}', color=GREEN), Spacer(1,.15*cm)]

    for key, title in [('career_path_advice','🚀 Career Path'),('salary_estimate','💰 Salary Estimate')]:
      if d.get(key):
        story += [H2(title), Body(d[key])]

    if d.get('linkedin_tips'):
      story.append(H2('🔗 LinkedIn Tips'))
      for tip in d['linkedin_tips']: story.append(Body(f'• {tip}'))

    if d.get('interview_questions'):
      story.append(H2('🎯 Likely Interview Questions'))
      for q in d['interview_questions']: story.append(Body(f'Q: {q}'))

    story += [Spacer(1,.5*cm), HRFlowable(width='100%',thickness=.5,color=colors.HexColor('#e8d8c0')), Small('Generated by Scorify.com')]
    doc.build(story)
    buf.seek(0)
    safe = cv.original_filename.rsplit('.',1)[0].replace(' ','_')
    resp = HttpResponse(buf, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="SCORIFY_{safe}_report.pdf"'
    return resp

  except ImportError:
    return JsonResponse({'error': 'Install reportlab: pip install reportlab --break-system-packages'}, status=500)
  except Exception as e:
    return JsonResponse({'error': f'PDF failed: {e}'}, status=500)


# ═══════════════════════════════════════════════════════════════════════════
# PAYMENT
# ═══════════════════════════════════════════════════════════════════════════

@login_required
@ensure_csrf_cookie
def upgrade_view(request):
  plan = request.GET.get('plan', 'pro')
  return render(request, 'roaster/upgrade.html', {'plan': plan, 'profile': _ensure_profile(request.user)})

@login_required
def payment_success(request):
  messages.success(request, ' Upgrade successful! Your new plan is active.')
  return redirect('dashboard')

@csrf_exempt
def paddle_webhook(request):
  if request.method != 'POST':
    return HttpResponse(status=405)
  try:
    import hashlib, hmac
    from django.conf import settings as django_settings
    from django.utils import timezone as tz

    data = request.POST.dict()
    alert_name = data.get('alert_name', '')

    if alert_name in ('payment_succeeded', 'subscription_created', 'subscription_payment_succeeded'):
      passthrough = json.loads(data.get('passthrough', '{}'))
      user_id = passthrough.get('user_id')
      plan = passthrough.get('plan', 'pro')
      sub_id = data.get('subscription_id', '')

      if user_id:
        user = User.objects.get(id=user_id)
        profile = _ensure_profile(user)
        profile.plan = plan
        profile.pro_since = tz.now()
        profile.save()
        send_pro_email(user)

    elif alert_name == 'subscription_cancelled':
      passthrough = json.loads(data.get('passthrough', '{}'))
      user_id = passthrough.get('user_id')
      if user_id:
        user = User.objects.get(id=user_id)
        profile = _ensure_profile(user)
        profile.plan = UserProfile.PLAN_FREE
        profile.save()

    elif alert_name == 'subscription_updated':
      passthrough = json.loads(data.get('passthrough', '{}'))
      user_id = passthrough.get('user_id')
      new_plan = passthrough.get('plan', 'pro')
      if user_id:
        profile = _ensure_profile(User.objects.get(id=user_id))
        profile.plan = new_plan
        profile.save()

    return HttpResponse(status=200)
  except Exception as e:
    print(f'[Webhook Error] {e}')
    return HttpResponse(status=200)

# ═══════════════════════════════════════════════════════════════════════════
# LEGAL PAGES
# ═══════════════════════════════════════════════════════════════════════════

def terms_view(request):
  profile = _ensure_profile(request.user) if request.user.is_authenticated else None
  return render(request, 'roaster/terms.html', {'profile': profile})


def privacy_view(request):
  profile = _ensure_profile(request.user) if request.user.is_authenticated else None
  return render(request, 'roaster/privacy.html', {'profile': profile})


def refund_view(request):
  profile = _ensure_profile(request.user) if request.user.is_authenticated else None
  return render(request, 'roaster/refund.html', {'profile': profile})