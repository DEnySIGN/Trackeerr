#!/usr/bin/env python3
"""Build only the public site; never copy files from the Android source repository."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import urllib.parse
import urllib.request

REPOSITORY = 'DEnySIGN/trackeerr'
PUBLIC_URL = f'https://github.com/{REPOSITORY}'
ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = (
    'index.html', 'confidentialite.html', '.nojekyll',
    'assets/site.css', 'assets/site.js',
    'assets/brand/logo-dark-compact.svg', 'assets/brand/logo-icon.svg',
    'assets/fonts/inter-latin.woff2', 'assets/fonts/OFL.txt',
    'assets/screenshots/accueil.png', 'assets/screenshots/serie.png', 'assets/screenshots/tracklist.png',
)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def api_get(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'Trackeerr-Pages', 'X-GitHub-Api-Version': '2022-11-28'}
    token = os.environ.get('GH_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    request = urllib.request.Request(f'https://api.github.com/{path}', headers=headers)
    with urllib.request.build_opener(NoRedirect).open(request, timeout=25) as response:
        return json.load(response)

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
                'sha256': digest[7:] if re.fullmatch(r'sha256:[a-fA-F0-9]{64}', digest) else None}
    return {'available': False}

def build(offline=False):
    repository = os.environ.get('GITHUB_REPOSITORY')
    if not offline and (not repository or repository.casefold() != REPOSITORY.casefold()):
        raise ValueError('Run in the public distribution repository, or use --offline for a local preview.')
    catalog = {'available': False} if offline else release_catalog(
        api_get(f'repos/{REPOSITORY}'), api_get(f'repos/{REPOSITORY}/releases?per_page=30'))
    destination = ROOT / 'dist'
    if destination.is_symlink():
        raise ValueError('The build directory must not be a symlink.')
    if destination.exists():
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
    print(f'Public site ready: {len(PUBLIC_FILES) + 1} files; APK available: {catalog["available"]}')
    return destination

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true', help='Preview the preparation state without a GitHub API request.')
    build(parser.parse_args().offline)
