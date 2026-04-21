/* ============================================================
   lang.js — Scorify
   Google Translate integration with custom Globe UI
   ============================================================ */

const LANGUAGES = [
  { code: 'en',    gtCode: null,   label: 'English',   flag: '🇬🇧' },
  { code: 'ar',    gtCode: 'ar',   label: 'العربية',   flag: '🇸🇦' },
  { code: 'fr',    gtCode: 'fr',   label: 'Français',  flag: '🇫🇷' },
  { code: 'es',    gtCode: 'es',   label: 'Español',   flag: '🇪🇸' },
  { code: 'de',    gtCode: 'de',   label: 'Deutsch',   flag: '🇩🇪' },
  { code: 'it',    gtCode: 'it',   label: 'Italiano',  flag: '🇮🇹' },
  { code: 'pt',    gtCode: 'pt',   label: 'Português', flag: '🇵🇹' },
  { code: 'tr',    gtCode: 'tr',   label: 'Türkçe',    flag: '🇹🇷' },
  { code: 'zh-CN', gtCode: 'zh-CN',label: '中文',       flag: '🇨🇳' },
  { code: 'ja',    gtCode: 'ja',   label: '日本語',     flag: '🇯🇵' },
];

/* ── Google Translate trigger ────────────────────────────── */
function translatePage(gtCode) {
  if (!gtCode) {
    // Restore original — remove cookie and reload
    document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=' + location.hostname;
    location.reload();
    return;
  }

  // Set Google Translate cookie
  const val = `/en/${gtCode}`;
  document.cookie = `googtrans=${val}; path=/`;
  document.cookie = `googtrans=${val}; path=/; domain=${location.hostname}`;

  // If Google Translate already loaded, use it directly
  const sel = document.querySelector('.goog-te-combo');
  if (sel) {
    sel.value = gtCode;
    sel.dispatchEvent(new Event('change'));
    return;
  }

  // Otherwise reload — GT widget will pick up the cookie
  location.reload();
}

function selectLang(code) {
  const lang = LANGUAGES.find(l => l.code === code);
  if (!lang) return;

  localStorage.setItem('scorify_lang', code);
  localStorage.setItem('scorify_lang_label', lang.flag + ' ' + lang.label);
  document.documentElement.lang = code;

  // Update RTL for Arabic immediately
  if (code === 'ar') {
    document.body.classList.add('rtl');
    document.body.style.direction = 'rtl';
    document.documentElement.dir = 'rtl';
  } else {
    document.body.classList.remove('rtl');
    document.body.style.direction = 'ltr';
    document.documentElement.dir = 'ltr';
  }

  translatePage(lang.gtCode);
  closeGlobe();
}

/* ── Build globe dropdown ────────────────────────────────── */
function buildGlobeBtn(containerId) {
  const wrap = document.getElementById(containerId);
  if (!wrap) return;

  const cur      = localStorage.getItem('scorify_lang') || 'en';
  const curLabel = localStorage.getItem('scorify_lang_label') || '🇬🇧 English';
  const curLang  = LANGUAGES.find(l => l.code === cur) || LANGUAGES[0];

  wrap.innerHTML = `
    <div style="position:relative;display:inline-block">
      <button type="button" id="globeBtn_${containerId}" onclick="toggleGlobe('${containerId}')"
        style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:99px;
               font-size:.78rem;font-weight:600;cursor:pointer;border:1px solid var(--border);
               background:rgba(255,255,255,.05);color:var(--smoke);transition:.25s;
               font-family:var(--font-m);white-space:nowrap"
        onmouseover="this.style.borderColor='var(--border2)';this.style.color='var(--cream)'"
        onmouseout="this.style.borderColor='var(--border)';this.style.color='var(--smoke)'">
        🌐 <span>${curLang.flag} ${curLang.label}</span>
      </button>
      <div id="globeDrop_${containerId}"
        style="display:none;position:absolute;top:calc(100% + 8px);right:0;
               background:var(--bg2);border:1px solid var(--border);border-radius:16px;
               padding:8px;min-width:180px;z-index:9999;
               box-shadow:0 16px 48px rgba(0,0,0,.6);backdrop-filter:blur(12px)">
        ${LANGUAGES.map(l => `
          <button type="button" onclick="selectLang('${l.code}')"
            style="display:flex;align-items:center;gap:10px;width:100%;padding:9px 14px;
                   border-radius:10px;border:none;
                   background:${l.code === cur ? 'rgba(255,77,0,.1)' : 'transparent'};
                   color:${l.code === cur ? 'var(--fire)' : 'var(--smoke)'};
                   cursor:pointer;font-size:.85rem;font-family:var(--font-b);
                   text-align:left;transition:.2s"
            onmouseover="this.style.background='rgba(255,77,0,.07)';this.style.color='var(--cream)'"
            onmouseout="this.style.background='${l.code === cur ? 'rgba(255,77,0,.1)' : 'transparent'}';
                        this.style.color='${l.code === cur ? 'var(--fire)' : 'var(--smoke)'}'">
            <span style="font-size:1.2rem">${l.flag}</span>
            <span>${l.label}</span>
            ${l.code === cur ? '<span style="margin-left:auto">✓</span>' : ''}
          </button>`).join('')}
      </div>
    </div>`;
}

function toggleGlobe(id) {
  document.querySelectorAll('[id^="globeDrop_"]').forEach(d => {
    if (d.id !== `globeDrop_${id}`) d.style.display = 'none';
  });
  const d = document.getElementById(`globeDrop_${id}`);
  if (d) d.style.display = d.style.display === 'none' ? 'block' : 'none';
}

function closeGlobe() {
  document.querySelectorAll('[id^="globeDrop_"]').forEach(d => d.style.display = 'none');
}

document.addEventListener('click', e => {
  if (!e.target.closest('[id^="globeBtn_"]') && !e.target.closest('[id^="globeDrop_"]')) closeGlobe();
});

/* ── Inject hidden Google Translate widget ───────────────── */
function injectGoogleTranslate() {
  if (document.getElementById('gt-script')) return;

  // Hidden container for GT widget
  const div = document.createElement('div');
  div.id = 'google_translate_element';
  div.style.cssText = 'position:absolute;top:-9999px;left:-9999px;visibility:hidden;height:0;overflow:hidden';
  document.body.appendChild(div);

  // GT init function
  window.googleTranslateElementInit = function() {
    new google.translate.TranslateElement(
      { pageLanguage: 'en', autoDisplay: false },
      'google_translate_element'
    );
  };

  // Load GT script
  const s = document.createElement('script');
  s.id  = 'gt-script';
  s.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
  document.head.appendChild(s);
}

/* ── Hide Google Translate top bar ──────────────────────── */
function hideGTBar() {
  const style = document.createElement('style');
  style.textContent = `
    .goog-te-banner-frame, .skiptranslate { display: none !important; }
    body { top: 0 !important; }
    .goog-tooltip, .goog-tooltip:hover { display: none !important; }
    .goog-text-highlight { background: none !important; box-shadow: none !important; }
    #goog-gt-tt { display: none !important; }
  `;
  document.head.appendChild(style);
}

/* ── Expose language for AI analysis ────────────────────── */
window.getAnalysisLang = function() {
  const code = localStorage.getItem('scorify_lang') || 'en';
  const lang = LANGUAGES.find(l => l.code === code);
  return lang ? lang.label : 'English';
};

/* ── Init ────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  hideGTBar();
  injectGoogleTranslate();

  // Build all globe buttons
  ['globeWrap','globeWrapNav','globeWrapAuth','globeWrapSb'].forEach(id => buildGlobeBtn(id));

  // Restore RTL if Arabic was selected
  const saved = localStorage.getItem('scorify_lang') || 'en';
  if (saved === 'ar') {
    document.body.classList.add('rtl');
    document.body.style.direction = 'rtl';
  }
});
