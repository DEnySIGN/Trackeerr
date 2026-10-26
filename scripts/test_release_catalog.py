import unittest
from build_site import release_catalog

class ReleaseCatalogTest(unittest.TestCase):
    public = {'full_name': 'DEnySIGN/trackeerr', 'private': False}
    def release(self, tag='v1', **extra):
        return dict({'published_at': '2026-10-26', 'draft': False, 'prerelease': False, 'tag_name': tag,
            'html_url': f'https://github.com/DEnySIGN/trackeerr/releases/tag/{tag}',
            'assets': [{'name': 'trackeerr.apk', 'state': 'uploaded',
                'browser_download_url': f'https://github.com/DEnySIGN/trackeerr/releases/download/{tag}/trackeerr.apk',
                'digest': 'sha256:' + 'a' * 64}]}, **extra)
    def test_only_the_public_distribution_repository_is_accepted(self):
        for metadata in [{'full_name': 'DEnySIGN/trackeerr', 'private': True}, {'full_name': 'someone/another', 'private': False}]:
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
        for url in ['https://example.com/app.apk', 'https://github.com/DEnySIGN/trackeerr/releases/download/../../app.apk']:
            release = self.release(); release['assets'][0]['browser_download_url'] = url
            with self.assertRaises(ValueError): release_catalog(self.public, [release])

if __name__ == '__main__': unittest.main()
