#!/usr/bin/env python3
"""Build only the public site; never copy files from the Android source repository."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import urllib.parse

REPOSITORY = 'DEnySIGN/Trackeerr'
PUBLIC_URL = f'https://github.com/{REPOSITORY}'
ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = (
    'index.html', 'confidentialite.html', 'guide.html', '.nojekyll',
    'assets/site.css', 'assets/site.js',
    'assets/brand/logo-dark-compact.svg', 'assets/brand/logo-icon.svg',
    'assets/fonts/inter-latin.woff2', 'assets/fonts/OFL.txt',
    'assets/screenshots/accueil.png', 'assets/screenshots/serie.png', 'assets/screenshots/tracklist.png',
    'assets/screenshots/mises-a-jour.png',
    'assets/licenses/Jellyfin-UX-CC-BY-SA-4.0.txt',
)

def api_get(path):
    if not path.startswith(f'repos/{REPOSITORY}'):
        raise ValueError('Only the public distribution repository is read.')
    result = subprocess.run(['gh', 'api', path, '-H', 'X-GitHub-Api-Version: 2022-11-28'],
                            check=True, capture_output=True, text=True, timeout=30)
    return json.loads(result.stdout)

def public_path(value, prefix):
    if not isinstance(value, str):
        return False
    parsed = urllib.parse.urlsplit(value)
    path = urllib.parse.unquote(parsed.path)
    return (parsed.scheme == 'https' and parsed.netloc == 'github.com' and
            not parsed.query and not parsed.fragment and path.startswith(f'/{REPOSITORY}/{prefix}') and
            '..' not in path.split('/'))

def release_catalog(metadata, releases):
    if metadata.get('private') is not False or metadata.get('full_name', '').casefold() != REPOSITORY.casefold():
        raise ValueError('The download catalog requires the public distribution repository.')
    published = [r for r in releases if not r.get('draft') and r.get('published_at')]
    candidates = [r for r in published if not r.get('prerelease')] + [r for r in published if r.get('prerelease')]
    for release in candidates:
        assets = [a for a in release.get('assets', []) if a.get('state') == 'uploaded' and
                  str(a.get('name', '')).lower().endswith('.apk')]
        if len(assets) != 1:
            continue
        asset = assets[0]
        if not public_path(asset.get('browser_download_url'), 'releases/download/'):
            raise ValueError('Unexpected APK download URL.')
        if not public_path(release.get('html_url'), 'releases/tag/'):
            raise ValueError('Unexpected release URL.')
        version = release.get('tag_name')
        if not isinstance(version, str) or not 1 <= len(version) <= 80:
            raise ValueError('Invalid version name.')
        digest = asset.get('digest') or ''
        return {'available': True, 'version': version, 'prerelease': bool(release.get('prerelease')),
                'apk': asset['browser_download_url'], 'page': release['html_url'],
                'bytes': asset.get('size'),
                'sha256': digest[7:] if re.fullmatch(r'sha256:[a-fA-F0-9]{64}', digest) else None}
    return {'available': False}

def update_catalog(catalog, distribution):
    absent = {'schemaVersion': 1, 'available': False}
    if not catalog.get('available') or catalog.get('prerelease'):
        return absent
    version = distribution.get('versionName', '')
    if catalog.get('version') != f'v{version}':
        return absent
    if not re.fullmatch(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', version):
        raise ValueError('Invalid stable version.')
    expected = f'{PUBLIC_URL}/releases/download/v{version}/trackeerr-{version}.apk'
    digest = catalog.get('sha256')
    if (catalog.get('apk') != expected or not isinstance(digest, str) or
            not re.fullmatch(r'[a-f0-9]{64}', digest) or digest != distribution.get('sha256') or
            catalog.get('bytes') != distribution.get('bytes') or not 0 < catalog['bytes'] <= 100*1024*1024):
        raise ValueError('The published APK must match the verified local distribution.')
    if (distribution.get('applicationId') != 'fr.trackeerr.app.cloudv2' or
            type(distribution.get('versionCode')) is not int or distribution['versionCode'] <= 0 or
            distribution.get('minSdk') != 26 or distribution.get('certificateSHA256') !=
            'f3743f0ac490d9fd17816217d3309d9fb2d439787a748185f148068f410c124f'):
        raise ValueError('Unexpected package identity or signing certificate.')
    return dict(schemaVersion=1, available=True, **{k: distribution[k] for k in
        ('applicationId','versionName','versionCode','minSdk','certificateSHA256','sha256','bytes')},
        apk=expected, page=f'{PUBLIC_URL}/releases/tag/v{version}')

def build(offline=False, pages=False):
    repository = os.environ.get('GITHUB_REPOSITORY')
    if not offline and repository and repository.casefold() != REPOSITORY.casefold():
        raise ValueError('Run in the public distribution repository, or use --offline for a local preview.')
    catalog = {'available': False} if offline else release_catalog(
        api_get(f'repos/{REPOSITORY}'), api_get(f'repos/{REPOSITORY}/releases?per_page=30'))
    update = update_catalog(catalog, json.loads((ROOT/'site/distribution.json').read_text()))
    destination = ROOT / ('docs' if pages else 'dist')
    if destination.is_symlink():
        raise ValueError('The build directory must not be a symlink.')
    if destination.exists():
        if pages:
            allowed = set(PUBLIC_FILES) | {'release.json','update.json'}
            if any(p.is_symlink() or p.is_file() and str(p.relative_to(destination)) not in allowed for p in destination.rglob('*')):
                raise ValueError('Refusing to replace an unmanaged Pages directory.')
        shutil.rmtree(destination)
    destination.mkdir()
    for relative in PUBLIC_FILES:
        source = ROOT / 'site' / relative
        if source.is_symlink() or not source.resolve().is_relative_to((ROOT / 'site').resolve()):
            raise ValueError('Public assets must stay inside the website directory.')
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (destination / 'release.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
    (destination / 'update.json').write_text(json.dumps(update, ensure_ascii=False, indent=2) + '\n')
    print(f'Public site ready: {len(PUBLIC_FILES) + 2} files; APK available: {catalog["available"]}; update feed: {update["available"]}')
    return destination

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true', help='Preview the preparation state without a GitHub API request.')
    parser.add_argument('--pages', action='store_true', help='Build the allowlisted public files into docs/ for branch-based GitHub Pages.')
    args = parser.parse_args()
    build(args.offline, args.pages)
