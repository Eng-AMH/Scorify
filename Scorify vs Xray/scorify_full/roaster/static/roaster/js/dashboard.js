/* ============================================================
 dashboard.js — Scorify
 Requires: shared.js loaded before this file
 Requires: window.SCORE_HISTORY and window.UPLOADS_TODAY
 set inline in dashboard.html
 ============================================================ */

/* ── LIMIT BAR ───────────────────────────────────────────── */
const lf = document.getElementById('limitFill');
if (lf) lf.style.width = Math.max(0, Math.min(100, (window.UPLOADS_TODAY / 3 * 100))) + '%';

/* ── SCORE CHART ─────────────────────────────────────────── */
const scoreData = window.SCORE_HISTORY || [];
if (scoreData.length && document.getElementById('scoreChart')) {
 const ctx = document.getElementById('scoreChart').getContext('2d');
 new Chart(ctx, {
 type: 'line',
 data: {
 labels: scoreData.map(d => d.date),
 datasets: [{
 label: 'Score',
 data: scoreData.map(d => d.score),
 borderColor: '#ff4d00',
 backgroundColor: 'rgba(255,77,0,.08)',
 borderWidth: 2,
 pointBackgroundColor: '#ffaa00',
 pointRadius: 4,
 pointHoverRadius: 6,
 tension: .4,
 fill: true
 }]
 },
 options: {
 responsive: true,
 maintainAspectRatio: false,
 plugins: {
 legend: { display: false },
 tooltip: {
 backgroundColor: '#110e09',
 borderColor: 'rgba(255,77,0,.3)',
 borderWidth: 1,
 titleColor: '#fff8ee',
 bodyColor: '#8a7a6a',
 padding: 10
 }
 },
 scales: {
 y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,.04)' }, ticks: { color: '#8a7a6a', font: { family: 'DM Mono', size: 11 } } },
 x: { grid: { color: 'rgba(255,255,255,.04)' }, ticks: { color: '#8a7a6a', font: { family: 'DM Mono', size: 11 } } }
 }
 }
 });
}

/* ── UPLOAD ZONE ─────────────────────────────────────────── */
const zone = document.getElementById('uploadZone');
const result = document.getElementById('resultArea');

if (zone) {
 zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag'); });
 zone.addEventListener('dragleave', () => zone.classList.remove('drag'));
 zone.addEventListener('drop', e => {
 e.preventDefault();
 zone.classList.remove('drag');
 if (e.dataTransfer.files[0]) doUpload(e.dataTransfer.files[0]);
 });
 zone.addEventListener('click', () => {
 const i = document.createElement('input');
 i.type = 'file';
 i.accept = '.pdf,.doc,.docx';
 i.onchange = e => doUpload(e.target.files[0]);
 i.click();
 });
}

async function doUpload(file) {
 document.getElementById('loadingEl')?.classList.add('show');
 const fd = new FormData();
 fd.append('cv_file', file);
 if (window.getAnalysisLang) fd.append('language', window.getAnalysisLang());
 try {
 const res = await fetch('/api/upload/', {
 method: 'POST',
 headers: { 'X-CSRFToken': getCookie('csrftoken') },
 body: fd
 });
 const d = await safeJson(res);
 if (!res.ok) {
 result.innerHTML = `<div style="padding:1rem;border:1px solid rgba(248,113,113,.3);border-radius:10px;color:#f87171;font-size:.875rem">${apiErrorMessage(d, 'Something went wrong.')}</div>`;
 return;
 }
 showQuickResult(d.analysis, file.name);
 setTimeout(() => location.reload(), 3500);
 } catch(e) {
 result.innerHTML = `<div style="color:#f87171;font-size:.875rem;padding:1rem">Error: ${e.message}</div>`;
 } finally {
 document.getElementById('loadingEl')?.classList.remove('show');
 }
}

function showQuickResult(an, fn) {
 const s = an.overall_score || 0, c = scoreColor(s);
 result.innerHTML = `
 <div style="display:flex;align-items:center;gap:1rem;padding:1rem;background:rgba(255,255,255,.03);border:1px solid var(--border);border-radius:12px">
 <div style="width:56px;height:56px;border-radius:50%;background:conic-gradient(${c} 0deg,${c} ${s*3.6}deg,rgba(255,255,255,.06) ${s*3.6}deg);display:flex;align-items:center;justify-content:center;position:relative;flex-shrink:0">
 <div style="position:absolute;inset:5px;background:var(--bg);border-radius:50%"></div>
 <span style="position:relative;font-family:var(--font-d);font-size:1.2rem;color:${c}">${s}</span>
 </div>
 <div style="flex:1;min-width:0">
 <div style="font-family:var(--font-d);font-size:1.2rem;color:var(--cream)">${an.verdict || ''}</div>
 <div style="font-size:.8rem;color:var(--smoke);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${(an.summary || '').substring(0, 90)}...</div>
 </div>
 <button class="view-btn" onclick="viewAnalysisData(${JSON.stringify(an).replace(/"/g,'&quot;')},'${fn.replace(/'/g,"\\'")}')">Full →</button>
 </div>
 <div style="font-size:.72rem;color:var(--smoke);text-align:center;margin-top:.5rem;font-family:var(--font-m)">Refreshing page in a moment...</div>`;
}

/* ── MODAL ───────────────────────────────────────────────── */
async function viewAnalysis(id) {
 try {
 const r = await fetch(`/api/analysis/${id}/`);
 const d = await safeJson(r);
 if (d.analysis) openModal(d.analysis, 'Analysis Report');
 else alert('Could not load analysis');
 } catch(e) { alert('Error loading analysis'); }
}

function viewAnalysisData(an, fn) { openModal(an, fn); }

function openModal(an, title) {
 document.getElementById('modalTitle').textContent = title || 'ANALYSIS';
 const s = an.overall_score || 0, c = scoreColor(s), deg = s * 3.6;
 const secs = an.sections || {}, rl = an.roast_lines || [], fixes = an.top_fixes || [], rws = an.rewrite_suggestions || [];

 document.getElementById('modalBody').innerHTML = `
 <div class="m-score-row">
 <div class="m-score-circle" style="background:conic-gradient(${c} 0deg,${c} ${deg}deg,rgba(255,255,255,.06) ${deg}deg)">
 <span style="color:${c}">${s}</span>
 </div>
 <div>
 <div style="font-family:var(--font-d);font-size:1.9rem;letter-spacing:.03em">${an.verdict || ''}</div>
 <div style="font-size:.9rem;color:var(--smoke);margin-top:.4rem;line-height:1.6">${an.summary || ''}</div>
 <div style="display:flex;gap:14px;margin-top:.75rem;flex-wrap:wrap">
 ${an.ats_score !== undefined ? `<span style="font-family:var(--font-m);font-size:.72rem;color:var(--smoke)">ATS: <strong style="color:${an.ats_score > 60 ? '#4ade80' : '#ffaa00'}">${an.ats_score}/100</strong></span>` : ''}
 ${an.language_quality !== undefined ? `<span style="font-family:var(--font-m);font-size:.72rem;color:var(--smoke)">Language: <strong style="color:var(--amber)">${an.language_quality}/100</strong></span>` : ''}
 ${an.estimated_interview_chance ? `<span style="font-family:var(--font-m);font-size:.72rem;color:var(--smoke)">Interview Chance: <strong style="color:var(--fire)">${an.estimated_interview_chance}</strong></span>` : ''}
 ${an.plan_used ? `<span class="plan-pill pp-${an.plan_used}">${an.plan_used.toUpperCase()}</span>` : ''}
 </div>
 </div>
 </div>
 ${Object.keys(secs).length ? `
 <div style="margin-bottom:1.5rem">
 <div style="font-family:var(--font-m);font-size:.62rem;color:var(--smoke);letter-spacing:.15em;text-transform:uppercase;margin-bottom:.75rem">SECTION SCORES</div>
 <div class="secs-grid">
 ${Object.entries(secs).map(([k, v]) => {
 const sc = v.score || 0, cc = sc < 40 ? '#f87171' : sc < 65 ? '#ffaa00' : '#4ade80';
 return `<div class="sec-item"><div class="sec-name">${k.replace(/_/g,' ').toUpperCase()}</div><div class="sec-bar-row"><div class="sec-track"><div class="sec-fill" style="width:${sc}%;background:${cc}"></div></div><div class="sec-num" style="color:${cc}">${sc}</div></div><div class="sec-fb">${v.feedback || ''}</div></div>`;
 }).join('')}
 </div>
 </div>` : ''}
 ${rl.length ? `
 <div style="margin-bottom:1.5rem">
 <div style="font-family:var(--font-m);font-size:.62rem;color:var(--smoke);letter-spacing:.15em;text-transform:uppercase;margin-bottom:.75rem">THE ROAST </div>
 ${rl.map(l => `<div class="roast-line rl-${l.type}"><span>${l.type === 'fire' ? '' : l.type === 'amber' ? '⚠️' : '✅'}</span><span>${l.text}</span></div>`).join('')}
 </div>` : ''}
 ${fixes.length ? `
 <div style="margin-bottom:1.5rem">
 <div style="font-family:var(--font-m);font-size:.62rem;color:var(--smoke);letter-spacing:.15em;text-transform:uppercase;margin-bottom:.75rem">TOP FIXES</div>
 ${fixes.map((f, i) => `<div style="display:flex;gap:.6rem;align-items:flex-start;margin-bottom:.4rem;font-size:.85rem;color:#b0a090;background:rgba(255,255,255,.025);border-radius:8px;padding:.6rem .875rem"><span style="color:var(--fire);font-weight:800;flex-shrink:0">${i+1}.</span><span>${f}</span></div>`).join('')}
 </div>` : ''}
 ${rws.length ? `<div class="vip-box"><div class="vip-box-title"> VIP: Rewrite Suggestions</div>${rws.map(r => `<div class="rw-card"><div class="rw-orig">❌ ${r.original}</div><div class="rw-impr">✅ ${r.improved}</div></div>`).join('')}</div>` : ''}
 ${an.career_path_advice ? `<div class="vip-box"><div class="vip-box-title">🎯 VIP: Career Path Advice</div><div style="font-size:.85rem;color:var(--smoke);line-height:1.65">${an.career_path_advice}</div></div>` : ''}
 ${an.salary_estimate ? `<div class="vip-box"><div class="vip-box-title">💰 VIP: Salary Estimate</div><div style="font-size:.85rem;color:var(--smoke)">${an.salary_estimate}</div></div>` : ''}
 ${an.interview_questions?.length ? `<div class="vip-box"><div class="vip-box-title">🎤 VIP: Interview Questions</div><ul class="vip-list">${an.interview_questions.map(q => `<li>${q}</li>`).join('')}</ul></div>` : ''}
 ${an.linkedin_tips?.length ? `<div class="vip-box"><div class="vip-box-title">💼 VIP: LinkedIn Tips</div><ul class="vip-list">${an.linkedin_tips.map(t => `<li>${t}</li>`).join('')}</ul></div>` : ''}
 ${an.industry_benchmark ? `<div class="vip-box"><div class="vip-box-title">📊 VIP: Industry Benchmark</div><div style="font-size:.85rem;color:var(--smoke)">${an.industry_benchmark}</div></div>` : ''}
 `;
 document.getElementById('modalBg')?.classList.add('open');
}

function closeModal() { document.getElementById('modalBg')?.classList.remove('open'); }
