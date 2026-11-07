"""Exercise decoding, verification, cancellation and preservation using synthetic data."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import sys
import unittest
from unittest.mock import patch

import patcher


class PatcherTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix='ct3-patcher-test-')
        self.root = Path(self.scratch.name)
        (self.root / 'patches').mkdir()
        (self.root / 'vendor').mkdir()
        shutil.copy2(patcher.ROOT / 'vendor/xdelta3.exe', self.root / 'vendor/xdelta3.exe')
        self.source = self.root / '원본 source.iso'
        self.source.write_bytes(bytes(range(256)) * 4096)
        self.target = self.root / 'target.iso'
        self.target.write_bytes(self.source.read_bytes()[:700000] + b'KOREAN PATCH TEST' * 15000)
        self.output = self.root / '한글 output.iso'
        subprocess.run([str(self.root / 'vendor/xdelta3.exe'), '-e', '-s', str(self.source),
                        str(self.target), str(self.root / 'patches/test.xdelta')], check=True,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))

        def meta(path):
            return {'file': str(path.relative_to(self.root)), 'bytes': path.stat().st_size,
                    'sha256': patcher.sha256(path)}

        self.manifest = {'version': 'test', 'source': meta(self.source), 'output': meta(self.target),
                         'patch': meta(self.root / 'patches/test.xdelta'),
                         'engine': meta(self.root / 'vendor/xdelta3.exe')}
        self.save_manifest()
        self.before = patcher.sha256(self.source)

    def save_manifest(self):
        (self.root / 'patches/manifest.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def tearDown(self):
        self.assertEqual(self.before, patcher.sha256(self.source))
        self.assertFalse(list(self.root.glob('*.partial')))
        self.scratch.cleanup()

    def test_roundtrip_with_korean_and_spaces(self):
        result = patcher.apply_patch(self.source, self.output, root=self.root)
        self.assertTrue(result['verified'])
        self.assertEqual(self.target.read_bytes(), self.output.read_bytes())

    def test_wrong_source_same_size_rejected(self):
        wrong = self.root / 'wrong.iso'
        wrong.write_bytes(b'X' * self.source.stat().st_size)
        with self.assertRaisesRegex(patcher.PatchError, 'SHA-256'):
            patcher.apply_patch(wrong, self.output, root=self.root)
        self.assertFalse(self.output.exists())

    def test_existing_output_preserved(self):
        self.output.write_bytes(b'keep this')
        with self.assertRaisesRegex(patcher.PatchError, '이미'):
            patcher.apply_patch(self.source, self.output, root=self.root)
        self.assertEqual(b'keep this', self.output.read_bytes())

    def test_source_as_output_rejected(self):
        with self.assertRaisesRegex(patcher.PatchError, '원본과 출력'):
            patcher.apply_patch(self.source, self.source, root=self.root)

    def test_corrupt_payload_rejected(self):
        (self.root / 'patches/test.xdelta').write_bytes(b'bad patch')
        with self.assertRaisesRegex(patcher.PatchError, '내장 패치'):
            patcher.apply_patch(self.source, self.output, root=self.root)

    def test_incorrect_result_not_published(self):
        self.manifest['output']['sha256'] = '0' * 64
        self.save_manifest()
        with self.assertRaisesRegex(patcher.PatchError, '결과 ISO'):
            patcher.apply_patch(self.source, self.output, root=self.root)
        self.assertFalse(self.output.exists())

    def test_cancel_during_decoding_removes_partial(self):
        cancel = threading.Event()

        def notify(label, value):
            if value >= 30:
                cancel.set()

        with self.assertRaises(patcher.Cancelled):
            patcher.apply_patch(self.source, self.output, root=self.root, cancel=cancel, notify=notify)
        self.assertFalse(self.output.exists())

    def test_low_space(self):
        with patch('patcher.shutil.disk_usage', return_value=shutil._ntuple_diskusage(1, 1, 0)):
            with self.assertRaisesRegex(patcher.PatchError, '빈 공간'):
                patcher.apply_patch(self.source, self.output, root=self.root)

    def test_destination_created_during_decode_survives(self):
        def notify(label, value):
            if value >= 75 and not self.output.exists():
                self.output.write_bytes(b'another process owns this')

        with self.assertRaises(OSError):
            patcher.apply_patch(self.source, self.output, root=self.root, notify=notify)
        self.assertEqual(b'another process owns this', self.output.read_bytes())

    def test_report_cannot_overwrite_original(self):
        with patch.object(sys, 'argv', ['patcher', '--self-test', '--report', str(self.source)]):
            self.assertEqual(1, patcher.main())
        self.assertEqual(self.before, patcher.sha256(self.source))

    def test_report_cannot_use_output_path(self):
        with patch.object(sys, 'argv', ['patcher', '--source', str(self.source),
                                      '--output', str(self.output), '--report', str(self.output)]):
            self.assertEqual(1, patcher.main())
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
