/* ============================================================
   profile.js — Scorify
   Profile page logic
   Requires: shared.js loaded before this file
   ============================================================ */

let newAvatarFile = null;

function previewAvatar(input) {
  const file = input.files[0];
  if (!file) return;
  if (file.size > 2 * 1024 * 1024) { alert('Image must be under 2MB'); return; }
  newAvatarFile = file;
  const reader = new FileReader();
  reader.onload = e => {
    const d = document.getElementById('avatarDisplay');
    d.innerHTML = `<img src="${e.target.result}" alt="" style="width:100%;height:100%;object-fit:cover">`;
  };
  reader.readAsDataURL(file);
}

async function saveProfile() {
  const form = document.getElementById('profileForm');
  const fd   = new FormData(form);
  if (newAvatarFile) fd.set('avatar', newAvatarFile);
  try {
    const r = await fetch('/profile/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      body: fd
    });
    const d = await safeJson(r);
    if (d.success) {
      const msg = document.getElementById('successMsg');
      msg.style.display = 'block';
      setTimeout(() => msg.style.display = 'none', 3000);
    }
  } catch(e) { alert('Error saving profile: ' + e.message); }
}
