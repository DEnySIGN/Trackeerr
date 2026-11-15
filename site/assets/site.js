'use strict';
document.documentElement.classList.add('js');
const menu = document.querySelector('.menu-button');
const navigation = document.querySelector('#navigation');
if (menu && navigation) {
  menu.hidden = false;
  const closeMenu = () => { menu.setAttribute('aria-expanded', 'false'); navigation.classList.remove('is-open'); };
  menu.addEventListener('click', () => { const open = menu.getAttribute('aria-expanded') !== 'true'; menu.setAttribute('aria-expanded', String(open)); navigation.classList.toggle('is-open', open); });
  navigation.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') { closeMenu(); menu.focus(); } });
}

function releaseUrl(value, kind = 'download') {
  if (typeof value !== 'string') return false;
  try {
    const url = new URL(value);
    const segments = url.pathname.split('/');
    return url.protocol === 'https:' && !url.username && !url.password && url.origin === 'https://github.com' &&
      value === url.href && decodeURIComponent(url.pathname) === url.pathname && !url.search && !url.hash &&
      segments[1] === 'DEnySIGN' && segments[2] === 'Trackeerr' && segments[3] === 'releases' &&
      (kind === 'download' ? segments.length === 7 && segments[4] === 'download' && /^v[0-9]+\.[0-9]+\.[0-9]+$/.test(segments[5]) && segments[6] === `trackeerr-${segments[5].slice(1)}.apk`
        : segments.length === 6 && segments[4] === 'tag' && /^v[0-9]+\.[0-9]+\.[0-9]+$/.test(segments[5]));
  } catch { return false; }
}
async function loadRelease() {
  const button = document.querySelector('#apk-download');
  if (!button) return;
  try {
    const response = await fetch('./release.json', { cache: 'no-cache', credentials: 'omit' });
    if (!response.ok) return;
    const release = await response.json();
    if (!release.available || !releaseUrl(release.apk) || typeof release.version !== 'string' || release.version.length > 80) return;
    document.querySelector('#release-title').textContent = `${release.prerelease ? 'Préversion' : 'Version'} ${release.version}`;
    document.querySelector('#release-description').textContent = 'Gratuit · Android 8.0 et plus. Téléchargement direct depuis GitHub.';
    button.href = release.apk; button.hidden = false;
    if (releaseUrl(release.page, 'page')) document.querySelector('#release-page').href = release.page;
    document.querySelector('#release-note').textContent = 'Retrouvez les changements et les instructions dans les notes de version.';
    if (typeof release.sha256 === 'string' && /^[a-f0-9]{64}$/i.test(release.sha256)) {
      document.querySelector('#checksum-value').textContent = release.sha256;
      document.querySelector('#checksum').hidden = false;
      document.querySelector('#copy-checksum').addEventListener('click', async () => {
        try { await navigator.clipboard.writeText(release.sha256); document.querySelector('#copy-status').textContent = 'Empreinte copiée.'; }
        catch { document.querySelector('#copy-status').textContent = 'Copie indisponible. Vous pouvez sélectionner et copier le texte ci-dessus.'; }
      });
    }
  } catch { /* The static preparation notice and GitHub link remain usable without a catalog. */ }
}
loadRelease();
