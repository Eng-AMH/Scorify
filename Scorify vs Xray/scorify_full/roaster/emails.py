from django.core.mail import send_mail
from django.conf import settings
import threading


def _send(subject, html, to):
  def _run():
    try:
      send_mail(subject=subject, message='', from_email=settings.DEFAULT_FROM_EMAIL,
           recipient_list=[to], html_message=html, fail_silently=False)
    except Exception as e:
      print(f"[Email Error] {e}")
  threading.Thread(target=_run, daemon=True).start()


def send_otp_email(email, code):
  html = f"""<!DOCTYPE html><html><body style="font-family:sans-serif;background:#0a0804;margin:0;padding:40px">
<div style="max-width:480px;margin:0 auto;background:linear-gradient(135deg,#ff4d00,#ffaa00);padding:3px;border-radius:20px">
<div style="background:#110e09;border-radius:18px;padding:40px;text-align:center">
<div style="font-size:2.5rem;margin-bottom:12px"></div>
<h1 style="color:#fff8ee;font-family:monospace;font-size:1.3rem;margin:0 0 8px;letter-spacing:.05em">SCORIFY</h1>
<p style="color:#8a7a6a;margin:0 0 28px;font-size:.9rem">Your verification code:</p>
<div style="background:#1a1208;border:2px solid #ff4d00;border-radius:16px;padding:28px;margin:0 0 24px">
<div style="font-family:monospace;font-size:3.5rem;font-weight:800;color:#ff4d00;letter-spacing:.4em">{code}</div>
</div>
<p style="color:#8a7a6a;font-size:.8rem;margin:0">Valid for 10 minutes · Do not share this code</p>
</div></div></body></html>"""
  _send(f" {code} — Your Scorify Code", html, email)


def send_welcome_email(user):
  html = f"""<!DOCTYPE html><html><body style="font-family:sans-serif;background:#0a0804;margin:0;padding:40px">
<div style="max-width:480px;margin:0 auto;background:linear-gradient(135deg,#ff4d00,#ffaa00);padding:3px;border-radius:20px">
<div style="background:#110e09;border-radius:18px;padding:40px;text-align:center">
<div style="font-size:2.5rem;margin-bottom:12px"></div>
<h1 style="color:#fff8ee;font-family:monospace;font-size:1.5rem;margin:0 0 8px">Welcome, {user.username}!</h1>
<p style="color:#8a7a6a;margin:0 0 28px">Your account is ready. Time to get roasted.</p>
<a href="{settings.SITE_URL}/dashboard/" style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#ff4d00,#ffaa00);color:#0a0804;border-radius:12px;font-weight:800;text-decoration:none;font-size:1rem"> Go to Dashboard</a>
<hr style="border:none;border-top:1px solid rgba(255,255,255,.07);margin:28px 0">
<p style="color:#8a7a6a;font-size:.8rem;margin:0">Free plan: 3 CVs/day · Upgrade anytime for unlimited</p>
</div></div></body></html>"""
  _send(" Welcome to Scorify!", html, user.email)


def send_pro_email(user):
  html = f"""<!DOCTYPE html><html><body style="font-family:sans-serif;background:#0a0804;margin:0;padding:40px">
<div style="max-width:480px;margin:0 auto;background:linear-gradient(135deg,#ff4d00,#ffaa00);padding:3px;border-radius:20px">
<div style="background:#110e09;border-radius:18px;padding:40px;text-align:center">
<div style="font-size:2.5rem;margin-bottom:12px">🏆</div>
<h1 style="color:#ff4d00;font-family:monospace;font-size:1.5rem;margin:0 0 8px">You're PRO now, {user.username}!</h1>
<p style="color:#8a7a6a;margin:0 0 20px">Unlimited uploads and full analysis unlocked.</p>
<div style="text-align:left;background:rgba(255,77,0,.06);border:1px solid rgba(255,77,0,.2);border-radius:12px;padding:20px;margin:0 0 24px">
<p style="color:#4ade80;margin:6px 0;font-size:.9rem">✓ Unlimited CV uploads</p>
<p style="color:#4ade80;margin:6px 0;font-size:.9rem">✓ Full section-by-section analysis</p>
<p style="color:#4ade80;margin:6px 0;font-size:.9rem">✓ AI rewrite suggestions</p>
<p style="color:#4ade80;margin:6px 0;font-size:.9rem">✓ Job description matching</p>
<p style="color:#4ade80;margin:6px 0;font-size:.9rem">✓ CV comparison tool</p>
<p style="color:#4ade80;margin:6px 0;font-size:.9rem">✓ PDF export reports</p>
</div>
<a href="{settings.SITE_URL}/dashboard/" style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#ff4d00,#ffaa00);color:#0a0804;border-radius:12px;font-weight:800;text-decoration:none"> Start Scoring</a>
</div></div></body></html>"""
  _send("🏆 You're now PRO — Scorify", html, user.email)


def send_weekly_digest(user, stats: dict):
  """
  Weekly progress digest email.
  stats = {
    'uploads_this_week': int,
    'best_score_this_week': int or None,
    'avg_score_this_week': float or None,
    'score_trend': 'up'|'down'|'neutral',
    'top_fix': str or None,
    'total_all_time': int,
  }
  """
  uploads = stats.get('uploads_this_week', 0)
  best = stats.get('best_score_this_week')
  avg = stats.get('avg_score_this_week')
  trend = stats.get('score_trend', 'neutral')
  top_fix = stats.get('top_fix', '')
  total = stats.get('total_all_time', 0)

  trend_icon = {'up': '📈', 'down': '📉', 'neutral': '➡️'}.get(trend, '➡️')
  trend_label = {'up': 'Improving!', 'down': 'Needs focus', 'neutral': 'Steady'}.get(trend, 'Steady')

  score_section = ""
  if best is not None:
    score_section = f"""
<div style="background:rgba(255,77,0,.06);border:1px solid rgba(255,77,0,.2);border-radius:12px;padding:20px;margin:16px 0;display:flex;gap:20px;flex-wrap:wrap">
 <div style="flex:1;text-align:center">
  <div style="font-size:2rem;font-weight:800;color:#ff4d00;font-family:monospace">{best}</div>
  <div style="font-size:.75rem;color:#8a7a6a">Best Score This Week</div>
 </div>
 {"" if avg is None else f'<div style="flex:1;text-align:center"><div style="font-size:2rem;font-weight:800;color:#ffaa00;font-family:monospace">{round(avg)}</div><div style="font-size:.75rem;color:#8a7a6a">Avg Score</div></div>'}
 <div style="flex:1;text-align:center">
  <div style="font-size:2rem">{trend_icon}</div>
  <div style="font-size:.75rem;color:#8a7a6a">{trend_label}</div>
 </div>
</div>"""

  top_fix_section = ""
  if top_fix:
    top_fix_section = f"""
<div style="background:rgba(74,222,128,.05);border:1px solid rgba(74,222,128,.2);border-radius:12px;padding:16px;margin:16px 0">
 <div style="font-size:.7rem;color:#4ade80;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px">💡 Top Fix From Your Last Analysis</div>
 <div style="color:#fff8ee;font-size:.9rem">{top_fix}</div>
</div>"""

  no_uploads_msg = ""
  if uploads == 0:
    no_uploads_msg = """
<div style="background:rgba(255,170,0,.05);border:1px solid rgba(255,170,0,.2);border-radius:12px;padding:16px;margin:16px 0;text-align:center">
 <div style="font-size:1.5rem;margin-bottom:6px">😴</div>
 <div style="color:#ffaa00;font-size:.9rem">No uploads this week — your CV isn't roasting itself!</div>
</div>"""

  html = f"""<!DOCTYPE html><html><body style="font-family:sans-serif;background:#0a0804;margin:0;padding:40px">
<div style="max-width:520px;margin:0 auto;background:linear-gradient(135deg,#ff4d00,#ffaa00);padding:3px;border-radius:20px">
<div style="background:#110e09;border-radius:18px;padding:40px">
 <div style="text-align:center;margin-bottom:24px">
  <div style="font-size:2rem;margin-bottom:8px"></div>
  <h1 style="color:#fff8ee;font-family:monospace;font-size:1.2rem;margin:0;letter-spacing:.05em">WEEKLY ROAST REPORT</h1>
  <p style="color:#8a7a6a;margin:4px 0 0;font-size:.85rem">Hey {user.username} — here's your week in review</p>
 </div>

 <div style="display:flex;gap:12px;margin-bottom:8px">
  <div style="flex:1;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:16px;text-align:center">
   <div style="font-size:1.8rem;font-weight:800;color:#fff8ee;font-family:monospace">{uploads}</div>
   <div style="font-size:.75rem;color:#8a7a6a">Uploads This Week</div>
  </div>
  <div style="flex:1;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:16px;text-align:center">
   <div style="font-size:1.8rem;font-weight:800;color:#fff8ee;font-family:monospace">{total}</div>
   <div style="font-size:.75rem;color:#8a7a6a">Total All Time</div>
  </div>
 </div>

 {score_section}
 {no_uploads_msg}
 {top_fix_section}

 <div style="text-align:center;margin-top:24px">
  <a href="{settings.SITE_URL}/dashboard/" style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#ff4d00,#ffaa00);color:#0a0804;border-radius:12px;font-weight:800;text-decoration:none;font-size:.95rem"> Upload This Week's CV</a>
 </div>

 <p style="text-align:center;color:#4a3a2a;font-size:.72rem;margin-top:24px;margin-bottom:0">
  You're receiving this because you have a Scorify account.<br>
  <a href="{settings.SITE_URL}/profile/" style="color:#4a3a2a">Manage preferences</a>
 </p>
</div></div></body></html>"""

  _send(" Your Weekly Roast Report", html, user.email)