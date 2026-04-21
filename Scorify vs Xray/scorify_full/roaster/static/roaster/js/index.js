/* ============================================================
 index.js — Scorify
 Landing page logic
 Requires: shared.js loaded before this file
 ============================================================ */

/* ── NAV SCROLL ──────────────────────────────────────────── */
addEventListener('scroll', () =>
 document.getElementById('navbar').classList.toggle('scrolled', scrollY > 30),
 { passive: true }
);

/* ── MOBILE BURGER MENU ──────────────────────────────────── */
(function () {
  const burger  = document.getElementById('navBurger');
  const drawer  = document.getElementById('navDrawer');
  const overlay = document.getElementById('navDrawerOverlay');
  if (!burger) return;

  function openMenu() {
    burger.classList.add('open');
    drawer.classList.add('open');
    overlay.classList.add('open');
    burger.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }
  function closeMenu() {
    burger.classList.remove('open');
    drawer.classList.remove('open');
    overlay.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }
  burger.addEventListener('click', () =>
    burger.classList.contains('open') ? closeMenu() : openMenu()
  );
  overlay.addEventListener('click', closeMenu);
  drawer.querySelectorAll('.nav-drawer-link').forEach(a =>
    a.addEventListener('click', closeMenu)
  );
  document.addEventListener('keydown', e => e.key === 'Escape' && closeMenu());
})();

/* ── SMOOTH SCROLL ───────────────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(a =>
 a.addEventListener('click', e => {
 const t = document.querySelector(a.getAttribute('href'));
 if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth' }); }
 })
);

/* ── SCROLL REVEAL ───────────────────────────────────────── */
const obs = new IntersectionObserver(ee => {
 ee.forEach(e => {
 if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
 });
}, { threshold: .07, rootMargin: '0px 0px -50px 0px' });
document.querySelectorAll('.reveal').forEach(el => obs.observe(el));

/* ── HERO PARALLAX ───────────────────────────────────────── */
addEventListener('scroll', () => {
 const h = document.querySelector('.hero-title');
 if (h) {
 h.style.transform = `translateY(${scrollY * .12}px)`;
 h.style.opacity = Math.max(0, 1 - scrollY / 600);
 }
}, { passive: true });

/* ── PARTICLES ───────────────────────────────────────────── */
(function () {
 const c = document.createElement('canvas');
 c.style.cssText = 'position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.55';
 document.body.prepend(c);
 const x = c.getContext('2d');
 let W, H;
 const rs = () => { W = c.width = innerWidth; H = c.height = innerHeight; };
 rs(); addEventListener('resize', rs, { passive: true });

 const P = Array.from({ length: 45 }, () => ({
 x: Math.random() * 1920, y: Math.random() * 1080,
 r: Math.random() * 1.4 + .3,
 vx: (Math.random() - .5) * .2, vy: -(Math.random() * .25 + .04),
 a: Math.random() * .45 + .08, ph: Math.random() * Math.PI * 2,
 col: Math.random() < .65 ? '255,77,0' : '255,170,0'
 }));

 let t = 0;
 (function loop() {
 x.clearRect(0, 0, W, H);
 P.forEach(p => {
 p.x += p.vx; p.y += p.vy;
 if (p.y < -20) { p.y = H + 20; p.x = Math.random() * W; }
 if (p.x < 0) p.x = W;
 if (p.x > W) p.x = 0;
 const a = p.a + Math.sin(t * .005 + p.ph) * .18;
 x.save();
 x.globalAlpha = Math.max(0, Math.min(.65, a));
 x.shadowBlur = 10; x.shadowColor = `rgba(${p.col},.7)`;
 x.beginPath(); x.arc(p.x, p.y, p.r * 2, 0, Math.PI * 2);
 x.fillStyle = `rgba(${p.col},1)`; x.fill(); x.restore();
 });
 t++; requestAnimationFrame(loop);
 })();
})();

/* ── LIVE STATS ──────────────────────────────────────────── */
fetch('/api/stats/').then(r => safeJson(r)).then(d => {
 if (d.total_roasted) {
 document.getElementById('tTotal').textContent = d.total_roasted.toLocaleString() + '+';
 document.getElementById('tAvg').textContent = d.average_score;
 }
}).catch(() => {});

/* ── UPLOAD ──────────────────────────────────────────────── */
const zone = document.getElementById('uploadZone');
const result = document.getElementById('resultArea');
const pill = document.getElementById('statusPill');

zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
zone.addEventListener('drop', e => {
 e.preventDefault(); zone.classList.remove('dragover');
 if (e.dataTransfer.files[0]) doUpload(e.dataTransfer.files[0]);
});
zone.addEventListener('click', () => {
 const i = document.createElement('input');
 i.type = 'file'; i.accept = '.pdf,.doc,.docx';
 i.onchange = e => doUpload(e.target.files[0]); i.click();
});

let pendingId = null;

async function doUpload(file) {
 document.getElementById('loadingEl').classList.add('show');
 pill.textContent = 'ANALYZING...'; pill.style.color = 'var(--amber)';
 const fd = new FormData(); fd.append('cv_file', file);
 if (window.getAnalysisLang) fd.append('language', window.getAnalysisLang());
 try {
 const res = await fetch('/api/upload/', {
 method: 'POST',
 headers: { 'X-CSRFToken': getCookie('csrftoken') },
 body: fd
 });
 const d = await safeJson(res);
 if (!res.ok) {
 if (d.error === 'upgrade_required') showUpgrade();
 else showErr(apiErrorMessage(d, 'Something went wrong'));
 pill.textContent = 'ERROR'; pill.style.color = '#f87171';
 return;
 }
 pendingId = d.analysis_id;
 renderResult(d.analysis, d.analysis_id, file.name, d.is_preview);
 pill.textContent = 'DONE ✓'; pill.style.color = '#4ade80';
 } catch(e) {
 showErr('Network error: ' + e.message);
 pill.textContent = 'ERROR'; pill.style.color = '#f87171';
 } finally {
 document.getElementById('loadingEl').classList.remove('show');
 }
}

function renderResult(an, id, fn, preview) {
 const s = an.overall_score || 0, c = scoreColor(s), deg = s * 3.6;
 const rl = an.roast_lines || [], fixes = an.top_fixes || [];
 result.innerHTML = `
 <div style="display:flex;align-items:center;gap:.875rem;margin-bottom:.875rem">
 <div style="width:72px;height:72px;border-radius:50%;background:conic-gradient(${c} 0deg,${c} ${deg}deg,rgba(255,255,255,.06) ${deg}deg);display:flex;align-items:center;justify-content:center;position:relative;flex-shrink:0">
 <div style="position:absolute;inset:6px;background:#0a0804;border-radius:50%"></div>
 <span style="position:relative;font-family:var(--font-d);font-size:1.5rem;color:${c}">${s}</span>
 </div>
 <div>
 <div style="font-size:.7rem;color:var(--smoke);font-family:var(--font-m);letter-spacing:.08em;margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px">${fn}</div>
 <div style="display:inline-block;padding:2px 10px;border-radius:99px;background:rgba(255,77,0,.12);border:1px solid rgba(255,77,0,.3);color:var(--fire);font-family:var(--font-m);font-size:.62rem;letter-spacing:.1em;margin-bottom:4px">${an.verdict || ''}</div>
 <div style="font-size:.8rem;color:var(--smoke);line-height:1.5">${(an.summary || '').substring(0, 110)}${(an.summary || '').length > 110 ? '...' : ''}</div>
 </div>
 </div>
 ${preview ? `<div style="background:rgba(255,77,0,.05);border:1px solid rgba(255,77,0,.2);border-radius:12px;padding:.875rem;text-align:center;margin-bottom:.75rem">
 <div style="font-weight:800;font-size:.85rem;color:var(--fire);margin-bottom:.35rem">🔒 Full Analysis Locked</div>
 <div style="font-size:.78rem;color:var(--smoke);margin-bottom:.75rem">Sign in to unlock section scores, ATS check, rewrite tips & more</div>
 <button onclick="openOTP('${id}',${s},'${(an.verdict || '').replace(/'/g,"\\'")}');return false" style="padding:8px 20px;border-radius:10px;background:linear-gradient(135deg,var(--fire),var(--amber));color:#0a0804;font-weight:800;border:none;cursor:pointer;font-size:.82rem"> Sign in & Unlock Free</button>
 </div>` : ''}
 <div style="display:flex;flex-direction:column;gap:.5rem">
 ${rl.slice(0, preview ? 2 : 8).map(l => `<div class="roast-line rl-${l.type}"><span>${l.type === 'fire' ? '' : l.type === 'amber' ? '⚠️' : '✅'}</span><span>${l.text}</span></div>`).join('')}
 ${preview && rl.length > 2 ? '<div class="roast-line rl-amber" style="opacity:.25;filter:blur(2.5px)"><span></span><span>More brutal feedback waiting behind sign-in...</span></div>' : ''}
 </div>
 ${!preview && fixes.length ? `<div style="margin-top:.875rem"><div style="font-family:var(--font-m);font-size:.62rem;color:var(--smoke);letter-spacing:.15em;text-transform:uppercase;margin-bottom:.5rem">Top Fixes</div>${fixes.map((f, i) => `<div style="display:flex;gap:.5rem;margin-bottom:.4rem;font-size:.82rem;color:#b0a090"><span style="color:var(--fire);font-weight:800;flex-shrink:0">${i+1}.</span><span>${f}</span></div>`).join('')}</div>` : ''}
 `;
 result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showErr(m) {
 result.innerHTML = `<div style="padding:1.5rem;border:1px solid rgba(248,113,113,.3);border-radius:12px;background:rgba(248,113,113,.04);text-align:center"><div style="color:#f87171;font-family:var(--font-d);font-size:1.1rem;margin-bottom:.4rem">ERROR</div><div style="font-size:.82rem;color:var(--smoke)">${m}</div></div>`;
}

function showUpgrade() {
 result.innerHTML = `<div style="padding:1.5rem;border:1px solid rgba(255,77,0,.3);border-radius:12px;background:rgba(255,77,0,.04);text-align:center"><div style="font-size:1.4rem;margin-bottom:.5rem"></div><div style="color:var(--fire);font-family:var(--font-d);font-size:1rem;margin-bottom:.4rem">FREE LIMIT REACHED</div><div style="font-size:.82rem;color:var(--smoke);margin-bottom:1rem">You've used your 3 free CVs today</div><a href="/upgrade/" style="display:inline-block;padding:10px 24px;border-radius:10px;background:linear-gradient(135deg,var(--fire),var(--amber));color:#0a0804;font-weight:800;text-decoration:none;font-size:.85rem">Upgrade to Pro →</a></div>`;
}

/* ── OTP MODAL ───────────────────────────────────────────── */
let otpEmail = null;

function openOTP(id, score, verdict) {
 pendingId = id;
 document.getElementById('prevScore').textContent = score;
 document.getElementById('prevVerdict').textContent = verdict;
 backToEmail();
 document.getElementById('otpOverlay').classList.add('open');
}

function closeOTP() { document.getElementById('otpOverlay').classList.remove('open'); }
function backToEmail() {
 document.getElementById('stepEmail').style.display = 'block';
 document.getElementById('stepCode').style.display = 'none';
 document.getElementById('otpErr').style.display = 'none';
}

async function sendOTP() {
 const em = document.getElementById('otpEmail').value.trim();
 if (!em || !em.includes('@') || !em.includes('.')) { otpErr('Please enter a valid email.'); return; }
 otpEmail = em;
 try {
 const r = await fetch('/api/send-otp/', {
 method: 'POST',
 headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
 body: JSON.stringify({ email: em, pending_analysis_id: pendingId })
 });
 const d = await safeJson(r);
 if (!r.ok) { otpErr(apiErrorMessage(d, 'Please try again.')); return; }
 document.getElementById('stepEmail').style.display = 'none';
 document.getElementById('stepCode').style.display = 'block';
 document.getElementById('otpMsg').textContent = 'Code sent to ' + em;
 document.getElementById('otpErr').style.display = 'none';
 setupDigits(); document.getElementById('d1').focus();
 } catch(e) { otpErr('Network error. Please try again.'); }
}

function setupDigits() {
 const ids = ['d1','d2','d3','d4','d5','d6'], ins = ids.map(i => document.getElementById(i));
 ins.forEach((inp, i) => {
 inp.value = '';
 inp.oninput = () => { inp.value = inp.value.replace(/\D/, ''); if (inp.value && i < 5) ins[i+1].focus(); };
 inp.onkeydown = e => { if (e.key === 'Backspace' && !inp.value && i > 0) ins[i-1].focus(); };
 });
}

async function verifyOTP() {
 const code = ['d1','d2','d3','d4','d5','d6'].map(i => document.getElementById(i).value).join('');
 if (code.length !== 6) { otpErr('Please enter the full 6-digit code.'); return; }
 try {
 const r = await fetch('/api/verify-otp/', {
 method: 'POST',
 headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
 body: JSON.stringify({ email: otpEmail, code })
 });
 const d = await safeJson(r);
 if (!r.ok) { otpErr(apiErrorMessage(d, 'Please try again.')); return; }
 if (d.analysis) { closeOTP(); renderResult(d.analysis, d.analysis_id, 'Your CV', false); }
 else window.location.href = d.redirect || '/dashboard/';
 } catch(e) { otpErr('Network error. Please try again.'); }
}

function otpErr(m) {
 const el = document.getElementById('otpErr');
 el.textContent = m; el.style.display = 'block';
}
