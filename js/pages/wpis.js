/* Sport Data – wpis blogowy: udostępnianie (kopiuj link, Facebook, LinkedIn) */
(() => {
  'use strict';

  const share = document.querySelector('[data-share]');
  if (!share) return;

  const url = location.href.split('#')[0];
  const status = share.querySelector('[data-share-status]');
  const copyBtn = share.querySelector('[data-share-copy]');
  const label = copyBtn?.querySelector('span');
  const defaultLabel = label?.textContent;
  let timer;

  // Linki do udostępniania – uzupełniamy adresem bieżącej strony
  const shareUrls = {
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
  };
  share.querySelectorAll('[data-share-net]').forEach((a) => {
    const href = shareUrls[a.dataset.shareNet];
    if (href) a.href = href; // otwiera się w nowej karcie (target="_blank" rel="noopener")
  });

  // Fallback dla przeglądarek bez Clipboard API / poza HTTPS
  const legacyCopy = (text) => {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0;';
    document.body.appendChild(ta);
    ta.select();
    let ok = false;
    try { ok = document.execCommand('copy'); } catch { ok = false; }
    ta.remove();
    return ok;
  };

  const feedback = (ok) => {
    clearTimeout(timer);
    const msg = ok ? 'Link skopiowany do schowka' : 'Nie udało się skopiować linku';
    if (status) status.textContent = msg;
    if (label) label.textContent = ok ? 'Skopiowano!' : 'Spróbuj ponownie';
    copyBtn.classList.toggle('is-copied', ok);
    timer = setTimeout(() => {
      if (label) label.textContent = defaultLabel;
      if (status) status.textContent = '';
      copyBtn.classList.remove('is-copied');
    }, 2500);
  };

  copyBtn?.addEventListener('click', async () => {
    let ok = false;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(url);
        ok = true;
      } else {
        ok = legacyCopy(url);
      }
    } catch {
      ok = legacyCopy(url);
    }
    feedback(ok);
  });
})();
