/* ============================================================
   auth.js — Scorify
   Login + Register page logic (both pages use this same file)
   Requires: shared.js loaded before this file
   ============================================================ */

let userEmail = null;

async function sendCode() {
  const em = document.getElementById('emailInput').value.trim();
  if (!em || !em.includes('@') || !em.includes('.')) { showErr('Please enter a valid email address.'); return; }
  userEmail = em;
  try {
    const r = await fetch('/api/send-otp/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify({ email: em })
    });
    const d = await safeJson(r);
    if (!r.ok) { showErr(apiErrorMessage(d, 'Please try again.')); return; }
    hideErr();
    document.getElementById('s1').classList.remove('active');
    document.getElementById('s2').classList.add('active');
    document.getElementById('codeSentMsg').textContent = 'We sent a 6-digit code to ' + em;
    setupDigits(); document.getElementById('d1').focus();
  } catch(e) { showErr('Network error. Please try again.'); }
}

function setupDigits() {
  const ids = ['d1','d2','d3','d4','d5','d6'], ins = ids.map(i => document.getElementById(i));
  ins.forEach((inp, i) => {
    inp.value = '';
    inp.oninput  = () => { inp.value = inp.value.replace(/\D/, ''); if (inp.value && i < 5) ins[i+1].focus(); };
    inp.onkeydown = e => {
      if (e.key === 'Backspace' && !inp.value && i > 0) ins[i-1].focus();
      if (e.key === 'Enter') verifyCode();
    };
  });
}

async function verifyCode() {
  const code = ['d1','d2','d3','d4','d5','d6'].map(i => document.getElementById(i).value).join('');
  if (code.length !== 6) { showErr('Please enter the full 6-digit code.'); return; }
  try {
    const r = await fetch('/api/verify-otp/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify({ email: userEmail, code })
    });
    const d = await safeJson(r);
    if (!r.ok) { showErr(apiErrorMessage(d, 'Please try again.')); return; }
    window.location.href = d.redirect || '/dashboard/';
  } catch(e) { showErr('Network error. Please try again.'); }
}

function goBack() {
  document.getElementById('s2').classList.remove('active');
  document.getElementById('s1').classList.add('active');
  hideErr();
}

function showErr(m) { const e = document.getElementById('errBox'); e.textContent = m; e.style.display = 'block'; }
function hideErr()  { document.getElementById('errBox').style.display = 'none'; }

document.getElementById('emailInput').addEventListener('keydown', e => { if (e.key === 'Enter') sendCode(); });
