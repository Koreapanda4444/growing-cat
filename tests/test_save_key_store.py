import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import save_key_store


class SaveKeyStoreTests(unittest.TestCase):
    @unittest.skipUnless(save_key_store._is_windows(), "DPAPI is Windows-only")
    def test_dpapi_round_trip_keeps_blob_buffers_alive(self):
        payload = b"growing-cat-test-key"

        protected = save_key_store._dpapi_protect(payload)
        restored = save_key_store._dpapi_unprotect(protected)

        self.assertNotEqual(protected, payload)
        self.assertEqual(restored, payload)

    def test_plain_key_file_round_trip_on_non_windows_path(self):
        original_paths = (save_key_store._APP_DIR, save_key_store._KEY_FILE)
        key = b"k" * 32

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            save_key_store._APP_DIR = root
            save_key_store._KEY_FILE = root / "save_hmac_key.bin"

            try:
                with patch("save_key_store._is_windows", return_value=False):
                    with patch("save_key_store.os.urandom", return_value=key):
                        self.assertEqual(save_key_store.get_or_create_hmac_key(), key)
                    self.assertEqual(save_key_store.load_hmac_key(), key)
                    self.assertEqual(save_key_store._KEY_FILE.read_bytes(), key)
            finally:
                save_key_store._APP_DIR, save_key_store._KEY_FILE = original_paths

    def test_load_hmac_key_returns_none_when_key_file_is_unreadable(self):
        original_paths = (save_key_store._APP_DIR, save_key_store._KEY_FILE)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            unreadable_path = root / "save_hmac_key.bin"
            unreadable_path.mkdir()
            save_key_store._APP_DIR = root
            save_key_store._KEY_FILE = unreadable_path

            try:
                with patch("save_key_store._is_windows", return_value=False):
                    self.assertIsNone(save_key_store.load_hmac_key())
            finally:
                save_key_store._APP_DIR, save_key_store._KEY_FILE = original_paths


if __name__ == "__main__":
    unittest.main()
