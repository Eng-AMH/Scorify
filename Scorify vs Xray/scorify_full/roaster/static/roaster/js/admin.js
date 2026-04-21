/* ============================================================
   admin.js — Scorify Custom Admin Panel
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ── Auto-dismiss success messages after 4s ── */
  document.querySelectorAll('.messagelist .success').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .5s, transform .5s';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-4px)';
      setTimeout(() => el.remove(), 500);
    }, 4000);
  });

  /* ── Confirm before bulk delete ── */
  const actionForm = document.querySelector('#changelist-form');
  if (actionForm) {
    actionForm.addEventListener('submit', e => {
      const action = actionForm.querySelector('select[name="action"]')?.value || '';
      if (!action.includes('delete')) return;
      const checked = document.querySelectorAll('input[name="_selected_action"]:checked').length;
      if (checked && !confirm(`⚠️ Delete ${checked} selected item(s)?\nThis cannot be undone.`)) {
        e.preventDefault();
      }
    });
  }

  /* ── Add row count badge to table header ── */
  const resultList = document.querySelector('#result_list');
  if (resultList) {
    const rows = resultList.querySelectorAll('tbody tr').length;
    const paginator = document.querySelector('.paginator');
    if (paginator && rows > 0) {
      const badge = document.createElement('span');
      badge.style.cssText = `
        display:inline-block; margin-left:8px;
        padding:2px 8px; border-radius:99px; font-size:.65rem;
        background:rgba(255,106,61,.15); color:#ff6a3d;
        border:1px solid rgba(255,106,61,.3); font-family:'DM Mono',monospace;
        letter-spacing:.05em; font-weight:700;
      `;
      badge.textContent = `${rows} rows`;
      paginator.prepend(badge);
    }
  }

  /* ── Make plan badges colorful in user lists ── */
  document.querySelectorAll('#result_list td').forEach(td => {
    const text = td.textContent.trim().toLowerCase();
    if      (text === 'vip')  { td.style.color = '#ff6a3d'; td.style.fontWeight = '700'; }
    else if (text === 'pro')  { td.style.color = '#3b82f6'; td.style.fontWeight = '700'; }
    else if (text === 'free') { td.style.color = '#94a3b8'; }
  });

  /* ── Score coloring in analysis tables ── */
  document.querySelectorAll('#result_list td').forEach(td => {
    const num = parseFloat(td.textContent.trim());
    if (!isNaN(num) && num >= 0 && num <= 100 && td.textContent.trim().length <= 3) {
      if      (num >= 70) { td.style.color = '#4ade80'; td.style.fontWeight = '700'; }
      else if (num >= 40) { td.style.color = '#8b5cf6'; td.style.fontWeight = '700'; }
      else                { td.style.color = '#f87171'; td.style.fontWeight = '700'; }
    }
  });

  /* ── Keyboard shortcut: / to focus search ── */
  document.addEventListener('keydown', e => {
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      const search = document.querySelector('#searchbar, input[type="search"]');
      if (search) search.focus();
    }
  });

  /* ── Copy cell value on double-click ── */
  document.querySelectorAll('#result_list td').forEach(td => {
    td.addEventListener('dblclick', () => {
      const text = td.textContent.trim();
      if (!text) return;
      navigator.clipboard?.writeText(text).then(() => {
        const original = td.style.background;
        td.style.transition = 'background .15s';
        td.style.background = 'rgba(74,222,128,.12)';
        setTimeout(() => { td.style.background = original; }, 600);
      });
    });
  });

});
