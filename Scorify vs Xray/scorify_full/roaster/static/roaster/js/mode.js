/* ============================================================
   mode.js — Scorify / Xray / S×X  |  3-Mode Engine
   AMH Systems  |  v2.0
   ============================================================ */

/* ── Content Dictionary ──────────────────────────────────── */
const MODES = {

  scorify: {
    key: 'scorify',
    bodyClass: 'scorify-mode',
    navIcon: 'S',
    logoSrc: '/static/roaster/img/logo-scorify.png',
    navText: 'Scorify',
    btnText: 'Scorify',
    heroTag:  'AI CV SCORING',
    heroLine1: 'TURN YOUR CV',
    heroLine2: 'INTO A SCORE.',
    heroSub:  'Get instant insights. Improve faster. Land better jobs.',
    heroCta1: 'Score My CV — Free',
    heroCta2: 'See How It Works →',
    demoBarLabel: 'scorify.app — scoring your CV',
    uploadDrop:   'Drop your CV here',
    uploadOr:     ' or click to browse',
    uploadHint:   'PDF or Word · Max 5MB · Free scoring',
    statusReady:  'READY TO SCORE',
    uploadDefault: 'Upload your CV to see your score',
    howLabel:  'The Process',
    howTitle:  'THREE STEPS TO YOUR SCORE',
    howSub:    'No guesswork. No fluff. Just your real score with what to fix.',
    step1Title: 'UPLOAD YOUR CV',
    step1Desc:  'Drop any PDF or Word file. Every language, every format.',
    step2Title: 'AI SCORES IT',
    step2Desc:  'Our AI reads every line and delivers your score in seconds.',
    step3Title: 'YOU IMPROVE IT',
    step3Desc:  'Get a prioritized fix list with exact rewrites to push your score higher.',
    featLabel: 'What We Score',
    featTitle: 'NOTHING GETS PAST US',
    featSub:   'Every section of your CV gets put under the scoring microscope.',
    feat1Title: 'IMPACT SCORE',
    feat1Desc:  'Vague fluff gets flagged. Quantified wins get rewarded. We know the difference.',
    feat2Title: 'ATS SCORE',
    feat2Desc:  'Know if your CV survives robot screeners before it reaches human eyes.',
    feat3Title: 'LANGUAGE SCORE',
    feat3Desc:  'Grammar, tone, clichés — all scored. Weak phrases get flagged instantly.',
    feat4Title: 'SECTION SCORE',
    feat4Desc:  'Every section — summary to skills — gets its own score and specific fix.',
    feat5Title: 'JOB MATCH',
    feat5Desc:  'Paste any job description. See exactly what you\'re missing.',
    feat6Title: 'INSTANT REWRITE',
    feat6Desc:  'Not just feedback — actual rewritten sentences ready to copy.',
    demoLabel: 'Try It Now',
    demoTitle: 'UPLOAD YOUR CV & GET SCORED',
    priceLabel: 'Simple Pricing',
    priceTitle: 'FREE TO SCORE, PAY TO REBUILD',
    priceSub:   'Start free. Upgrade when you\'re ready to get serious.',
    ctaTitle:   'READY TO SCORE YOUR CV?',
    ctaSpan:    'Score Higher.',
    ctaSub:     'Join 47,000+ job seekers who already got their score.',
    ctaBtn:     'Score My CV Now',
    verdictBad:  'NEEDS WORK',
    verdictMid:  'GETTING THERE',
    verdictGood: 'HIGH SCORE',
    tickerAction: 'CVs Scored',
    tickerProblem: 'Generic Objective Statement',
    tickerImprove: '+34 points after fixes',
    loadingTitle: 'SCORING...',
    loadingSub:   'processing your document',
    sampleName1: "Ahmed's CV",
    sampleName2: "Sara's CV",
    sampleName3: "John's CV",
  },

  xray: {
    key: 'xray',
    bodyClass: 'xray-mode',
    navIcon: 'X',
    logoSrc: '/static/roaster/img/logo-xray.png',
    btnText: 'Xray Scan',
    heroTag:  'AI CV ANALYSIS',
    heroLine1: 'SEE EVERYTHING.',
    heroLine2: 'IMPROVE EVERYTHING.',
    heroSub:  'X-ray view of your CV. Deep analysis. Smarter decisions.',
    heroCta1: 'Scan My CV — Free',
    heroCta2: 'View Capabilities →',
    demoBarLabel: 'xray.engine — scanning document',
    uploadDrop:   'Submit CV for analysis',
    uploadOr:     ' or drag to this zone',
    uploadHint:   'PDF or Word · Max 5MB · Deep scan mode',
    statusReady:  'SCAN READY',
    uploadDefault: 'Submit your CV to initiate deep scan',
    howLabel:  'Scan Protocol',
    howTitle:  'THREE PHASES OF ANALYSIS',
    howSub:    'Systematic. Precise. No CV defect goes undetected.',
    step1Title: 'SUBMIT DOCUMENT',
    step1Desc:  'Input any PDF or Word document. All formats processed at the byte level.',
    step2Title: 'DEEP SCAN',
    step2Desc:  'Multi-layer AI analysis: ATS layer, semantic layer, impact layer — all in parallel.',
    step3Title: 'REVIEW FINDINGS',
    step3Desc:  'Receive a structured diagnostic report with severity-ranked recommendations.',
    featLabel: 'Analysis Modules',
    featTitle: 'FULL SPECTRUM DIAGNOSTICS',
    featSub:   'Every layer of your CV is scanned with surgical precision.',
    feat1Title: 'IMPACT ANALYSIS',
    feat1Desc:  'Semantic impact scoring. Achievement density mapped. Quantification index calculated.',
    feat2Title: 'ATS DIAGNOSTICS',
    feat2Desc:  'Full ATS simulation. Keyword density mapped. Parser compatibility tested.',
    feat3Title: 'LINGUISTIC SCAN',
    feat3Desc:  'Passive voice detected. Cliché density measured. Clarity index generated.',
    feat4Title: 'STRUCTURE MAP',
    feat4Desc:  'Section topology analyzed. Hierarchy and flow defects identified precisely.',
    feat5Title: 'JOB FIT MATRIX',
    feat5Desc:  'Multi-dimensional job description alignment. Gap analysis with priority ranking.',
    feat6Title: 'REWRITE ENGINE',
    feat6Desc:  'AI-generated replacement text. Optimized variants for each weak section.',
    demoLabel: 'Initiate Scan',
    demoTitle: 'SUBMIT DOCUMENT FOR ANALYSIS',
    priceLabel: 'Access Tiers',
    priceTitle: 'BASIC SCAN OR FULL DIAGNOSTIC',
    priceSub:   'Choose your depth of analysis.',
    ctaTitle:   'INITIATE YOUR CV ANALYSIS',
    ctaSpan:    'See Everything.',
    ctaSub:     '47,000+ documents scanned. Uncover what\'s holding you back.',
    ctaBtn:     'Start Deep Scan',
    verdictBad:  'CRITICAL GAPS',
    verdictMid:  'PARTIAL MATCH',
    verdictGood: 'STRONG SIGNAL',
    tickerAction: 'CVs Scanned',
    tickerProblem: 'Missing Keyword Density',
    tickerImprove: '+34 ATS points after optimization',
    loadingTitle: 'SCANNING...',
    loadingSub:   'running deep analysis',
    sampleName1: 'Document #A-42',
    sampleName2: 'Document #B-17',
    sampleName3: 'Document #C-91',
  },

  sx: {
    key: 'sx',
    bodyClass: 'sx-mode',
    navIcon: 'S×X',
    logoSrc: '/static/roaster/img/logo-sx.png',
    btnText: 'S×X Engine',
    heroTag:  'HYBRID INTELLIGENCE ENGINE',
    heroLine1: 'SCORE IT.',
    heroLine2: 'X-RAY IT.',
    heroSub:  'The full Scorify + Xray engine combined. Maximum intelligence. Deepest analysis. Elite results.',
    heroCta1: 'Unlock S×X Engine',
    heroCta2: 'View Pro Features →',
    demoBarLabel: 'sx.engine — hybrid analysis active',
    uploadDrop:   'Submit CV to S×X Engine',
    uploadOr:     ' or drag here',
    uploadHint:   'PDF or Word · Max 5MB · Full hybrid analysis',
    statusReady:  'S×X READY',
    uploadDefault: 'Submit your CV for full hybrid analysis',
    howLabel:  'Hybrid Protocol',
    howTitle:  'LIGHT MEETS SIGNAL',
    howSub:    'Score it with Scorify. Scan it with Xray. Get results nothing else can match.',
    step1Title: 'SUBMIT DOCUMENT',
    step1Desc:  'One upload activates both engines simultaneously. Full parallel processing.',
    step2Title: 'DUAL ENGINE',
    step2Desc:  'Scorify scores every dimension. Xray scans every layer. Both run at once.',
    step3Title: 'ELITE REPORT',
    step3Desc:  'A unified report combining score data + deep diagnostics + elite recommendations.',
    featLabel: 'Hybrid Capabilities',
    featTitle: 'THE MOST POWERFUL CV ANALYSIS',
    featSub:   'Everything from both engines. Nothing held back.',
    feat1Title: 'HYBRID IMPACT',
    feat1Desc:  'Scorify scoring + Xray semantic analysis = the most accurate impact measurement ever.',
    feat2Title: 'FULL ATS SUITE',
    feat2Desc:  'ATS scoring (Scorify) + ATS simulation (Xray). The deepest ATS analysis available.',
    feat3Title: 'ELITE LANGUAGE',
    feat3Desc:  'Language scoring + linguistic scanning combined. Zero weak copy survives.',
    feat4Title: 'MASTER STRUCTURE',
    feat4Desc:  'Score your structure AND get a full diagnostic map. The complete picture.',
    feat5Title: 'PRECISION JOB FIT',
    feat5Desc:  'Job match scoring + multi-dimensional alignment matrix. Pro-level targeting.',
    feat6Title: 'ELITE REWRITE',
    feat6Desc:  'Rewrite suggestions optimized for both ATS algorithms and human readers.',
    demoLabel: 'S×X Engine',
    demoTitle: 'ACTIVATE FULL HYBRID ANALYSIS',
    priceLabel: 'Pro Access',
    priceTitle: 'UNLOCK THE FULL S×X ENGINE',
    priceSub:   'S×X is included in Pro. One plan, both engines, maximum power.',
    ctaTitle:   'UNLOCK THE S×X ENGINE',
    ctaSpan:    'Maximum Power.',
    ctaSub:     'Pro users get both engines. The most powerful CV analysis ever built.',
    ctaBtn:     'Unlock S×X — Go Pro',
    verdictBad:  'CRITICAL — FULL SCAN',
    verdictMid:  'PARTIAL — NEEDS WORK',
    verdictGood: 'ELITE LEVEL',
    tickerAction: 'Hybrid Analyses',
    tickerProblem: 'Low ATS + Impact Score',
    tickerImprove: '+48 combined score after S×X',
    loadingTitle: 'S×X ENGINE...',
    loadingSub:   'dual engine analysis running',
    sampleName1: 'Hybrid Scan #A',
    sampleName2: 'Hybrid Scan #B',
    sampleName3: 'Hybrid Scan #C',
  }
};

/* ── State ───────────────────────────────────────────────── */
const STORAGE_KEY = 'scorify_mode';
const THEME_KEY   = 'scorify_theme';
let currentMode  = 'scorify';
let isProUser    = false;   /* will be set from Django context */

/* ── Init ────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  /* Read pro status from DOM if available */
  const proEl = document.getElementById('userIsPro');
  if (proEl) isProUser = proEl.dataset.pro === 'true';

  /* Restore saved mode */
  const saved = localStorage.getItem(STORAGE_KEY) || 'scorify';
  applyMode(saved, false);

  /* Build mode selector buttons if present */
  buildModeSelector();

  /* Apply saved theme (light/dark) */
  applyTheme(localStorage.getItem(THEME_KEY) || 'dark');
});

/* ── Build mode selector ─────────────────────────────────── */
function buildModeSelector() {
  const containers = document.querySelectorAll('.mode-selector');
  containers.forEach(sel => {
    sel.innerHTML = '';
    Object.values(MODES).forEach(m => {
      const btn = document.createElement('button');
      btn.className = 'mode-btn';
      btn.dataset.mode = m.key;
      if (m.key === 'sx') {
        btn.innerHTML = `<span class="mode-dot"></span>S/X <span class="mode-pro-badge">PRO</span>`;
      } else {
        btn.innerHTML = `<span class="mode-dot"></span>${m.key.charAt(0).toUpperCase() + m.key.slice(1)}`;
      }
      btn.addEventListener('click', () => switchMode(m.key));
      sel.appendChild(btn);
    });
  });
}

/* ── Switch mode (public) ────────────────────────────────── */
function switchMode(modeKey) {
  if (!MODES[modeKey]) return;

  /* S/X pro gate */
  if (modeKey === 'sx' && !isProUser) {
    showSxGate();
    return;
  }

  applyMode(modeKey, true);
}

/* ── Apply mode ──────────────────────────────────────────── */
function applyMode(modeKey, animate) {
  if (!MODES[modeKey]) modeKey = 'scorify';
  currentMode = modeKey;
  localStorage.setItem(STORAGE_KEY, modeKey);

  const mode = MODES[modeKey];
  const body = document.body;

  /* transition class for smooth CSS changes */
  if (animate) {
    body.classList.add('mode-changing');
    setTimeout(() => body.classList.remove('mode-changing'), 500);
  }

  /* Remove all mode classes, add new one */
  body.classList.remove('scorify-mode', 'xray-mode', 'sx-mode');
  body.classList.add(mode.bodyClass);

  /* Update content via data attributes */
  updateContent(mode);

  /* Update mode selector buttons */
  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.mode === modeKey);
  });

  /* Update brand marks everywhere — swap logo image src */
  const brandIcons = document.querySelectorAll('.nav-logo-icon, .auth-brand-mark, .auth-logo-icon, .sb-logo-icon, .otp-logo-icon, .footer-logo-icon, .legal-logo-icon, .loading-fire');
  brandIcons.forEach(el => {
    const img = el.querySelector('img.mode-logo-img');
    if (img) {
      img.src = mode.logoSrc;
    } else {
      /* fallback for any icon not yet upgraded to img */
      el.textContent = mode.navIcon;
    }
  });
  const logoText = document.querySelector('.nav-logo-text');
  if (logoText) logoText.textContent = mode.navText;

  /* Update primary CTA button */
  const navBtn = document.getElementById('navModeBtn');
  if (navBtn) navBtn.textContent = mode.btnText;

  /* Update loading overlay */
  const loadTitle = document.querySelector('.loading-title');
  if (loadTitle) loadTitle.textContent = mode.loadingTitle;
  const loadSub = document.querySelector('.loading-sub');
  if (loadSub) loadSub.textContent = mode.loadingSub;

  /* Fire event for page-specific JS */
  document.dispatchEvent(new CustomEvent('modechange', { detail: { mode: modeKey, data: mode } }));
}

/* ── Content updater ─────────────────────────────────────── */
function updateContent(mode) {
  const map = {
    'hero-tag':        mode.heroTag,
    'hero-line1':      mode.heroLine1,
    'hero-line2':      mode.heroLine2,
    'hero-sub':        mode.heroSub,
    'hero-cta1':       mode.heroCta1,
    'hero-cta2':       mode.heroCta2,
    'demo-bar-label':  mode.demoBarLabel,
    'upload-drop':     mode.uploadDrop,
    'upload-or':       mode.uploadOr,
    'upload-hint':     mode.uploadHint,
    'status-ready':    mode.statusReady,
    'upload-result-default': mode.uploadDefault,
    'how-label':       mode.howLabel,
    'how-title':       mode.howTitle,
    'how-sub':         mode.howSub,
    'step1-title':     mode.step1Title,
    'step1-desc':      mode.step1Desc,
    'step2-title':     mode.step2Title,
    'step2-desc':      mode.step2Desc,
    'step3-title':     mode.step3Title,
    'step3-desc':      mode.step3Desc,
    'feat-label':      mode.featLabel,
    'feat-title':      mode.featTitle,
    'feat-sub':        mode.featSub,
    'feat1-title':     mode.feat1Title,
    'feat1-desc':      mode.feat1Desc,
    'feat2-title':     mode.feat2Title,
    'feat2-desc':      mode.feat2Desc,
    'feat3-title':     mode.feat3Title,
    'feat3-desc':      mode.feat3Desc,
    'feat4-title':     mode.feat4Title,
    'feat4-desc':      mode.feat4Desc,
    'feat5-title':     mode.feat5Title,
    'feat5-desc':      mode.feat5Desc,
    'feat6-title':     mode.feat6Title,
    'feat6-desc':      mode.feat6Desc,
    'demo-label':      mode.demoLabel,
    'demo-title':      mode.demoTitle,
    'price-label':     mode.priceLabel,
    'price-title':     mode.priceTitle,
    'price-sub':       mode.priceSub,
    'verdict-bad':     mode.verdictBad,
    'verdict-mid':     mode.verdictMid,
    'verdict-good':    mode.verdictGood,
    'ticker-action':   mode.tickerAction,
    'ticker-problem':  mode.tickerProblem,
    'ticker-improve':  mode.tickerImprove,
    'sample-name1':    mode.sampleName1,
    'sample-name2':    mode.sampleName2,
    'sample-name3':    mode.sampleName3,
    'cta-title-text':  mode.ctaTitle,
    'cta-span-text':   mode.ctaSpan,
    'cta-sub-text':    mode.ctaSub,
    'cta-btn-text':    mode.ctaBtn,
  };

  Object.entries(map).forEach(([key, value]) => {
    document.querySelectorAll(`[data-mode-key="${key}"]`).forEach(el => {
      el.textContent = value;
    });
    /* also support old data-i18n keys for backwards compat */
    document.querySelectorAll(`[data-i18n="${key}"]`).forEach(el => {
      el.textContent = value;
    });
  });

  /* Update heroBtn id reference */
  const heroBtn = document.getElementById('heroBtn');
  if (heroBtn) heroBtn.textContent = mode.heroCta1;
}

/* ── S/X Pro Gate modal ──────────────────────────────────── */
function showSxGate() {
  const existing = document.getElementById('sxGateModal');
  if (existing) { existing.classList.add('open'); return; }

  const overlay = document.createElement('div');
  overlay.id = 'sxGateModal';
  overlay.style.cssText = `
    position:fixed;inset:0;z-index:9000;
    background:rgba(7,3,14,.92);backdrop-filter:blur(16px);
    display:flex;align-items:center;justify-content:center;
    padding:2rem;animation:fadeUp .3s ease both;
  `;

  overlay.innerHTML = `
    <div style="
      background:#0e0619;
      border:1px solid rgba(192,132,252,.3);
      border-radius:28px;
      padding:3rem 2.5rem;
      max-width:480px;width:100%;
      text-align:center;
      position:relative;
      box-shadow:0 40px 80px rgba(0,0,0,.8),0 0 60px rgba(192,132,252,.15);
    ">
      <!-- animated gradient top line -->
      <div style="position:absolute;top:0;left:0;right:0;height:2px;border-radius:28px 28px 0 0;
        background:linear-gradient(90deg,#ff4d00,#c084fc,#00d4ff,#c084fc,#ff4d00);
        background-size:400% 400%;animation:sxBorder 4s ease infinite;"></div>

      <div style="font-size:3.5rem;margin-bottom:1rem;filter:drop-shadow(0 0 20px rgba(192,132,252,.7))">⚡</div>

      <div style="font-family:'Orbitron',sans-serif;font-size:1.6rem;letter-spacing:.08em;margin-bottom:.5rem;
        background:linear-gradient(135deg,#ff4d00,#c084fc,#00d4ff);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
        S/X ENGINE
      </div>

      <div style="font-family:'DM Mono',monospace;font-size:.72rem;letter-spacing:.15em;
        text-transform:uppercase;color:#8060aa;margin-bottom:1.5rem;">
        PRO EXCLUSIVE · HYBRID INTELLIGENCE
      </div>

      <div style="background:rgba(192,132,252,.06);border:1px solid rgba(192,132,252,.15);
        border-radius:16px;padding:1.25rem;margin-bottom:1.75rem;">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.75rem;text-align:left;">
          ${['Full Scorify Engine','Full Xray Engine','Hybrid Impact Score','Elite ATS Suite','Precision Job Fit','Elite Rewrite Engine'].map(f =>
            `<div style="display:flex;align-items:center;gap:8px;font-size:.8rem;color:#c4b0d8;">
              <span style="color:#c084fc;font-size:.9rem">✦</span>${f}
            </div>`
          ).join('')}
        </div>
      </div>

      <a href="/upgrade/?plan=pro" class="btn btn-fire btn-lg" style="width:100%;justify-content:center;
        background:linear-gradient(135deg,#ff4d00,#c084fc,#00d4ff);
        box-shadow:0 8px 32px rgba(192,132,252,.4);">
        ⚡ Unlock S/X — Go Pro
      </a>
      <div style="margin-top:1rem;font-size:.75rem;color:#8060aa;font-family:'DM Mono',monospace;">
        Pro unlocks advanced hybrid analysis · Cancel anytime
      </div>

      <button onclick="document.getElementById('sxGateModal').classList.remove('open');this.closest('#sxGateModal').remove();"
        style="position:absolute;top:1rem;right:1rem;background:rgba(255,255,255,.05);
          border:1px solid rgba(255,255,255,.1);color:#8060aa;width:30px;height:30px;
          border-radius:8px;cursor:pointer;display:flex;align-items:center;justify-content:center;
          font-size:.9rem;transition:.2s;">×</button>
    </div>
  `;

  overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });
  document.body.appendChild(overlay);

  /* add needed keyframe if missing */
  if (!document.getElementById('sx-border-kf')) {
    const s = document.createElement('style');
    s.id = 'sx-border-kf';
    s.textContent = '@keyframes sxBorder{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}';
    document.head.appendChild(s);
  }
}

/* ── Theme (light/dark) ──────────────────────────────────── */
function syncThemeButtons(theme) {
  const icon  = theme === 'light' ? '🌙' : '☀️';
  const label = theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode';
  document.querySelectorAll('[data-theme-toggle], #themeBtn').forEach(btn => {
    btn.textContent = icon;
    btn.setAttribute('aria-label', label);
    btn.setAttribute('aria-pressed', String(theme === 'light'));
  });
}

function applyTheme(theme) {
  const t = theme === 'light' ? 'light' : 'dark';
  document.body.classList.toggle('light-mode', t === 'light');
  document.documentElement.dataset.theme = t;
  localStorage.setItem(THEME_KEY, t);
  syncThemeButtons(t);
}

function toggleTheme() {
  const cur = localStorage.getItem(THEME_KEY) || 'dark';
  applyTheme(cur === 'dark' ? 'light' : 'dark');
}

/* expose globally */
window.switchMode   = switchMode;
window.toggleTheme  = toggleTheme;
window.applyTheme   = applyTheme;
window.applyMode    = applyMode;
window.showSxGate   = showSxGate;
window.MODES        = MODES;
