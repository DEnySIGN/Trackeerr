"""Transfer a verified APK via temporary draft assets; never publish a release.

Small uploads use the Cloud's dedicated upload secret. Assembly runs on GitHub
with the workflow token. No Android source, signing key or Actions artifact.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request

REPO = 'DEnySIGN/Trackeerr'
CHUNK = 1024 * 1024
FACTS = Path(__file__).resolve().parents[1] / 'site/distribution.json'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def sha(data):
    return hashlib.sha256(data).hexdigest()


def api(path, method='GET'):
    return json.loads(subprocess.check_output(['gh', 'api', '--method', method,
                                              f'repos/{REPO}/{path}'], text=True) or 'null')


def upload(release_id, name, data, credential):
    url = f'https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets?'
    url += urllib.parse.urlencode({'name': name})
    request = urllib.request.Request(url, data=data, method='POST', headers={
        'Authorization': 'Bearer ' + credential,
        'Content-Type': 'application/octet-stream',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'})
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f'Upload rejected: HTTP {error.code}, asset {name}') from None


def verify_asset(asset, data):
    if (asset.get('state') != 'uploaded' or asset.get('size') != len(data)
            or asset.get('digest') != 'sha256:' + sha(data)):
        raise ValueError('Asset differs from expected bytes: ' + asset.get('name', '?'))


def draft(release_id, facts):
    release = api(f'releases/{release_id}')
    if not release['draft'] or release['tag_name'] != 'v' + facts['versionName']:
        raise ValueError('Expected matching draft release')
    return release


def transfer_manifest(data, name):
    return {'name': name, 'size': len(data), 'sha256': sha(data),
            'parts': [{'name': name + f'.part-{i:04d}', 'size': len(part), 'sha256': sha(part)}
                      for i, part in enumerate(data[n:n + CHUNK] for n in range(0, len(data), CHUNK))]}


def validate_manifest(manifest, facts):
    name = f"trackeerr-{facts['versionName']}.apk"
    if (manifest['name'] != name or manifest['size'] != facts['bytes']
            or manifest['sha256'] != facts['sha256']):
        raise ValueError('Transfer does not match committed distribution facts')
    parts = manifest['parts']
    if len(parts) != math.ceil(facts['bytes'] / CHUNK):
        raise ValueError('Incorrect part count')
    for i, part in enumerate(parts):
        expected_size = min(CHUNK, facts['bytes'] - i * CHUNK)
        if (part['name'] != name + f'.part-{i:04d}' or part['size'] != expected_size
                or len(part['sha256']) != 64
                or any(c not in '0123456789abcdef' for c in part['sha256'])):
            raise ValueError('Invalid part description')


def download(asset, folder):
    # gh handles GitHub's authenticated release download and CDN redirect.
    destination = folder / str(asset['id'])
    with destination.open('wb') as output:
        subprocess.run(['gh', 'api', f"repos/{REPO}/releases/assets/{asset['id']}",
                        '--header', 'Accept: application/octet-stream'], stdout=output, check=True)
    data = destination.read_bytes()
    verify_asset(asset, data)
    return data


def stage(release_id, apk):
    facts = json.loads(FACTS.read_text())
    data = apk.read_bytes()
    if len(data) != facts['bytes'] or sha(data) != facts['sha256']:
        raise ValueError('APK differs from verified distribution facts')
    name = f"trackeerr-{facts['versionName']}.apk"
    manifest = transfer_manifest(data, name)
    validate_manifest(manifest, facts)
    assets = {a['name']: a for a in draft(release_id, facts)['assets']}
    if name in assets:
        verify_asset(assets[name], data)
        print('Final APK already present and verified')
        return
    credential = os.environ['TRACKEERR_GITHUB_RELEASE_TOKEN']
    for i, part in enumerate(manifest['parts']):
        payload = data[i * CHUNK:(i + 1) * CHUNK]
        asset = assets.get(part['name'])
        if asset is None:
            asset = upload(release_id, part['name'], payload, credential)
        verify_asset(asset, payload)
        print(f"Verified part {i + 1}/{len(manifest['parts'])}", flush=True)
    name = name + '.transfer.json'
    payload = json.dumps(manifest, sort_keys=True).encode()
    asset = assets.get(name)
    if asset is None:
        asset = upload(release_id, name, payload, credential)
    verify_asset(asset, payload)
    print('Transfer ready; draft remains unpublished')


def assemble(release_id):
    if os.environ.get('GITHUB_REPOSITORY') != REPO or os.environ.get('GITHUB_ACTIONS') != 'true':
        raise ValueError('Assembly is restricted to the repository workflow')
    facts = json.loads(FACTS.read_text())
    name = f"trackeerr-{facts['versionName']}.apk"
    assets = {a['name']: a for a in draft(release_id, facts)['assets']}
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        manifest_asset = assets[name + '.transfer.json']
        if manifest_asset['size'] > 16384:
            raise ValueError('Transfer manifest too large')
        manifest = json.loads(download(manifest_asset, folder))
        validate_manifest(manifest, facts)
        data = bytearray()
        cleanup = []
        for part in manifest['parts']:
            asset = assets[part['name']]
            if asset['size'] != part['size'] or asset['digest'] != 'sha256:' + part['sha256']:
                raise ValueError('Part metadata differs from manifest')
            data.extend(download(asset, folder))
            cleanup.append(asset['id'])
        if len(data) != facts['bytes'] or sha(data) != facts['sha256']:
            raise ValueError('Assembled APK differs from committed distribution facts')
        # Recheck draft before attaching, and never replace a different APK.
        current = {a['name']: a for a in draft(release_id, facts)['assets']}
        asset = current.get(name)
        if asset is None:
            asset = upload(release_id, name, bytes(data), os.environ['GH_TOKEN'])
        verify_asset(asset, data)
        if download(asset, folder) != data:
            raise ValueError('Final downloaded APK differs')
        for asset_id in cleanup + [manifest_asset['id']]:
            api(f'releases/assets/{asset_id}', method='DELETE')
        print(f'APK attached and downloaded bytes verified: {name}, {len(data)} bytes, SHA-256 {sha(data)}')
        print('Temporary transfer assets removed. Release remains draft.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['stage', 'assemble'])
    parser.add_argument('--release-id', required=True, type=int)
    parser.add_argument('--apk', type=Path)
    args = parser.parse_args()
    if args.release_id <= 0:
        parser.error('Positive release ID required')
    if args.operation == 'stage':
        if not args.apk:
            parser.error('--apk required for staging')
        stage(args.release_id, args.apk)
    else:
        assemble(args.release_id)
