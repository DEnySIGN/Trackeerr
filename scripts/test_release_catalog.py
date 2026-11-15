import unittest
from build_site import release_catalog, update_catalog

class ReleaseCatalogTest(unittest.TestCase):
    public = {'full_name': 'DEnySIGN/Trackeerr', 'private': False}
    def release(self, tag='v1', **extra):
        return dict({'published_at': '2026-10-26', 'draft': False, 'prerelease': False, 'tag_name': tag,
            'html_url': f'https://github.com/DEnySIGN/Trackeerr/releases/tag/{tag}',
            'assets': [{'name': 'trackeerr.apk', 'state': 'uploaded',
                'browser_download_url': f'https://github.com/DEnySIGN/Trackeerr/releases/download/{tag}/trackeerr.apk',
                'digest': 'sha256:' + 'a' * 64}]}, **extra)
    def test_only_the_public_distribution_repository_is_accepted(self):
        for metadata in [{'full_name': 'DEnySIGN/Trackeerr', 'private': True}, {'full_name': 'someone/another', 'private': False}]:
            with self.assertRaises(ValueError): release_catalog(metadata, [self.release()])
    def test_empty_and_draft_only_releases_keep_the_preparation_notice(self):
        self.assertEqual({'available': False}, release_catalog(self.public, []))
        self.assertEqual({'available': False}, release_catalog(self.public, [self.release(draft=True)]))
    def test_a_stable_apk_is_preferred_to_a_newer_prerelease(self):
        result = release_catalog(self.public, [self.release('v2', prerelease=True), self.release('v1')])
        self.assertEqual('v1', result['version']); self.assertEqual('a' * 64, result['sha256'])
    def test_a_prerelease_is_identified_when_no_stable_release_exists(self):
        self.assertTrue(release_catalog(self.public, [self.release(prerelease=True)])['prerelease'])
    def test_ambiguous_apks_and_releases_without_apks_are_not_selected(self):
        release = self.release()
        release['assets'] *= 2
        self.assertEqual({'available': False}, release_catalog(self.public, [release, self.release(assets=[])]))
    def test_unexpected_download_origins_and_parent_paths_are_rejected(self):
        for url in ['https://example.com/app.apk', 'https://github.com/DEnySIGN/Trackeerr/releases/download/../../app.apk']:
            release = self.release(); release['assets'][0]['browser_download_url'] = url
            with self.assertRaises(ValueError): release_catalog(self.public, [release])

    def distribution(self):
        return dict(applicationId='fr.trackeerr.app.cloudv2',versionName='0.6.54',versionCode=61,minSdk=26,
            certificateSHA256='f3743f0ac490d9fd17816217d3309d9fb2d439787a748185f148068f410c124f',sha256='a'*64,bytes=14_000_000)
    def catalog(self):
        return dict(available=True,prerelease=False,version='v0.6.54',sha256='a'*64,bytes=14_000_000,
            apk='https://github.com/DEnySIGN/Trackeerr/releases/download/v0.6.54/trackeerr-0.6.54.apk')
    def test_update_feed_is_absent_until_the_matching_stable_apk_is_published(self):
        for c in [dict(available=False),dict(self.catalog(),prerelease=True),dict(self.catalog(),version='v0.6.53')]:
            self.assertEqual(dict(schemaVersion=1,available=False),update_catalog(c,self.distribution()))
    def test_update_feed_uses_the_verified_package_version_certificate_and_digest(self):
        result=update_catalog(self.catalog(),self.distribution())
        self.assertEqual(61,result['versionCode']);self.assertEqual('a'*64,result['sha256'])
        self.assertEqual('https://github.com/DEnySIGN/Trackeerr/releases/tag/v0.6.54',result['page'])
    def test_a_different_published_binary_or_identity_never_produces_an_update(self):
        for field,value in [('sha256','b'*64),('bytes',15),('apk','https://evil.invalid/a.apk')]:
            with self.assertRaises(ValueError): update_catalog(dict(self.catalog(),**{field:value}),self.distribution())
        for field,value in [('applicationId','wrong.package'),('versionCode',False),('minSdk',21),('certificateSHA256','b'*64)]:
            with self.assertRaises(ValueError): update_catalog(self.catalog(),dict(self.distribution(),**{field:value}))

if __name__ == '__main__': unittest.main()
