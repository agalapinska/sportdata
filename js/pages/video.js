/* Sport Data – odtwarzacz wideo „click-to-load” (strona O nas)
 * Markup: <div class="video" data-video data-video-src="…" [data-video-poster="…"] [data-video-title="…"]>
 *           <button class="video__play">…</button><p class="video__msg" role="status"></p></div>
 * data-video-src: link YouTube (watch?v=, youtu.be/, /embed/, /shorts/) lub plik wideo (.mp4/.webm).
 * Zewnętrzny odtwarzacz ładuje się dopiero po kliknięciu (brak ruchu do YouTube przed zgodą użytkownika).
 */
(() => {
  'use strict';

  const youtubeId = (url) => {
    const m = url.match(/(?:youtube(?:-nocookie)?\.com\/(?:watch\?(?:.*&)?v=|embed\/|shorts\/|live\/)|youtu\.be\/)([\w-]{11})/i);
    return m ? m[1] : null;
  };

  document.querySelectorAll('[data-video]').forEach((box) => {
    const btn = box.querySelector('.video__play');
    const msg = box.querySelector('.video__msg');
    const poster = box.dataset.videoPoster;
    if (poster) box.style.setProperty('--video-poster', `url("${poster}")`);

    btn?.addEventListener('click', () => {
      const src = (box.dataset.videoSrc || '').trim();
      const title = box.dataset.videoTitle || 'Wideo';
      if (!src) {
        if (msg) msg.textContent = 'Film będzie dostępny wkrótce.';
        return;
      }

      let player;
      const id = youtubeId(src);
      if (id) {
        player = document.createElement('iframe');
        player.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0&modestbranding=1`;
        player.title = title;
        player.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
        player.allowFullscreen = true;
        player.referrerPolicy = 'strict-origin-when-cross-origin';
      } else {
        player = document.createElement('video');
        player.src = src;
        player.controls = true;
        player.autoplay = true;
        player.playsInline = true;
        if (poster) player.poster = poster;
        player.setAttribute('aria-label', title);
      }
      player.className = 'video__player';
      box.classList.add('is-playing');
      btn.replaceWith(player);
      if (msg) msg.textContent = '';
      player.focus?.();
    });
  });
})();
