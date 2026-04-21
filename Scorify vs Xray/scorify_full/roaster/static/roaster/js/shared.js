/* ============================================================
 shared.js — Scorify
 Helper functions shared across ALL pages
 ============================================================ */

/** Read a cookie value by name */
function getCookie(name) {
 const v = `; ${document.cookie}`;
 const p = v.split(`; ${name}=`);
 if (p.length === 2) return p.pop().split(';').shift();
 return '';
}

/** Return hex color based on CV score */
function scoreColor(s) {
 return s < 40 ? '#f87171' : s < 65 ? '#ffaa00' : '#4ade80';
}

/** Return class name (fire / amber / green) based on CV score */
function scoreClass(s) {
 return s < 40 ? 'fire' : s < 65 ? 'amber' : 'green';
}

/** Show a toast notification */
function toast(msg, type = 'success') {
 const t = document.createElement('div');
 const c = type === 'error' ? '#f87171' : type === 'warning' ? '#ffaa00' : '#4ade80';
 t.style.cssText = `
 position:fixed;bottom:2rem;right:2rem;z-index:9999;
 background:#110e09;border:1px solid ${c};border-radius:12px;
 padding:14px 20px;font-size:.875rem;color:${c};
 box-shadow:0 8px 30px rgba(0,0,0,.5);
 animation:slideIn .3s cubic-bezier(.34,1.56,.64,1);
 max-width:320px;font-family:'Bricolage Grotesque',sans-serif;
 `;
 t.textContent = msg;
 document.body.appendChild(t);
 setTimeout(() => {
 t.style.opacity = '0';
 t.style.transition = 'opacity .3s';
 setTimeout(() => t.remove(), 300);
 }, 3000);
}

/** Safely parse an API response as JSON without throwing on HTML/error pages */
async function safeJson(response) {
 const text = await response.text();
 if (!text) return {};
 try {
 return JSON.parse(text);
 } catch {
 return { raw: text };
 }
}


/** Normalize API error payloads into a readable message */
function apiErrorMessage(data, fallback = 'Something went wrong.') {
 return data?.message || data?.error || data?.detail || data?.raw || fallback;
}


/** Helper: normalize a pathname (remove trailing slash except root) */
function normalizePath(pathname) {
 return pathname && pathname !== '/' ? pathname.replace(/\/+$/, '') : '/';
}

/** Set the active sidebar link based on the current page. */
function syncSidebarActiveLink() {
 const links = Array.from(document.querySelectorAll('.sidebar .sb-nav .sb-link'));
 if (!links.length) return;

 const currentPath = normalizePath(window.location.pathname);

 links.forEach((link) => link.classList.remove('active'));

 let matched = false;
 for (const link of links) {
 const href = link.getAttribute('href') || '';
 if (!href || href.startsWith('#')) continue;

 // Ignore fragment links like /dashboard/#uploadZone
 const url = new URL(href, window.location.origin);
 if (url.hash) continue;

 const linkPath = normalizePath(url.pathname);
 if (linkPath === currentPath) {
 link.classList.add('active');
 matched = true;
 break;
 }
 }

 // Keep no item highlighted on pages outside the sidebar cluster.
 return matched;
}

/** Mobile sidebar drawer used by dashboard/profile/compare. */
function initMobileSidebar() {
 const sidebar = document.querySelector('.sidebar');
 const toggle = document.querySelector('[data-sidebar-toggle]');
 const overlay = document.querySelector('[data-sidebar-overlay]');
 if (!sidebar || !toggle || !overlay) return;

 const setOpen = (open) => {
 document.body.classList.toggle('sidebar-open', open);
 sidebar.classList.toggle('open', open);
 overlay.classList.toggle('active', open);
 toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
 toggle.textContent = open ? 'X' : '⋮';
 };

 const close = () => setOpen(false);
 const open = () => setOpen(true);

 toggle.addEventListener('click', () => {
 const isOpen = document.body.classList.contains('sidebar-open');
 setOpen(!isOpen);
 });

 overlay.addEventListener('click', close);

 document.querySelectorAll('.sidebar a').forEach((link) => {
 link.addEventListener('click', () => {
 if (window.innerWidth <= 768) close();
 });
 });

 window.addEventListener('resize', () => {
 if (window.innerWidth > 768) close();
 });

 window.addEventListener('keydown', (e) => {
 if (e.key === 'Escape') close();
 });

 // Keep the initial icon correct even if CSS shows the button on mobile.
 toggle.setAttribute('aria-expanded', 'false');
 toggle.textContent = '⋮';
}

document.addEventListener('DOMContentLoaded', () => {
 syncSidebarActiveLink();
 initMobileSidebar();
});
