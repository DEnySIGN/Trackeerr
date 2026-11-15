import copy
import unittest
from unittest.mock import patch
import release_transfer as t


class ReleaseTransferTest(unittest.TestCase):
    def setUp(self):
        self.data = b'a' * (t.CHUNK + 7)
        self.facts = {'versionName': '0.6.54', 'bytes': len(self.data), 'sha256': t.sha(self.data)}
        self.manifest = t.transfer_manifest(self.data, 'trackeerr-0.6.54.apk')

    def test_round_trip_boundaries(self):
        t.validate_manifest(self.manifest, self.facts)
        self.assertEqual([p['size'] for p in self.manifest['parts']], [t.CHUNK, 7])
        self.assertEqual(len(set(p['name'] for p in self.manifest['parts'])), 2)

    def test_rejects_wrong_distribution_or_parts(self):
        for key, value in [('sha256', 'f' * 64), ('size', 2), ('name', '../other.apk'), ('parts', [])]:
            bad = copy.deepcopy(self.manifest)
            bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                t.validate_manifest(bad, self.facts)
        for key, value in [('name', '../part'), ('size', 4), ('sha256', 'z' * 64)]:
            bad = copy.deepcopy(self.manifest)
            bad['parts'][0][key] = value
            with self.subTest(part=key), self.assertRaises(ValueError):
                t.validate_manifest(bad, self.facts)

    def test_asset_requires_uploaded_size_and_digest(self):
        good = {'name': 'file', 'state': 'uploaded', 'size': len(self.data), 'digest': 'sha256:' + t.sha(self.data)}
        t.verify_asset(good, self.data)
        for key, value in [('state', 'starter'), ('size', 1), ('digest', None)]:
            bad = dict(good, **{key: value})
            with self.subTest(key=key), self.assertRaises(ValueError):
                t.verify_asset(bad, self.data)

    def test_only_matching_draft_accepted(self):
        for draft, tag in [(False, 'v0.6.54'), (True, 'v0.6.53')]:
            with patch.object(t, 'api', return_value={'draft': draft, 'tag_name': tag}), self.assertRaises(ValueError):
                t.draft(1, self.facts)

    def test_assemble_requires_github_workflow(self):
        with patch.dict(t.os.environ, {}, clear=True), self.assertRaises(ValueError):
            t.assemble(1)
