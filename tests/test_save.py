import tempfile
import unittest
from pathlib import Path

import save
import save_key_store


class SaveRoundTripTests(unittest.TestCase):
    def test_signed_save_round_trip_in_temp_directory(self):
        payload = {
            "day": 3,
            "time_phase": "morning",
            "difficulty": "normal",
            "personality": "energetic",
            "money": 42,
            "inventory": {"사료": 1},
            "minigame_used": {"jump": False},
            "cat": {
                "name": "nabi",
                "stage": "아기고양이",
                "hunger": 30,
                "tiredness": 20,
                "happiness": 70,
                "cleanliness": 80,
            },
        }

        original_save_paths = (
            save._DATA_DIR,
            save.SAVE_FILE,
            save._LEGACY_APPDATA_JSON,
            save._LEGACY_CWD_JSON,
        )
        original_key_paths = (save_key_store._APP_DIR, save_key_store._KEY_FILE)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            save._DATA_DIR = root
            save.SAVE_FILE = str(root / "save.dat")
            save._LEGACY_APPDATA_JSON = str(root / "save.json")
            save._LEGACY_CWD_JSON = str(root / "cwd-save.json")
            save_key_store._APP_DIR = root
            save_key_store._KEY_FILE = root / "save_hmac_key.bin"

            try:
                self.assertTrue(save.save_game(payload))
                self.assertEqual(save.load_game(), payload)
            finally:
                (
                    save._DATA_DIR,
                    save.SAVE_FILE,
                    save._LEGACY_APPDATA_JSON,
                    save._LEGACY_CWD_JSON,
                ) = original_save_paths
                save_key_store._APP_DIR, save_key_store._KEY_FILE = original_key_paths

    def test_failed_atomic_write_removes_temp_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "save.dat"

            with self.assertRaises(TypeError):
                save._write_json_atomic(str(path), {"bad": object()})

            self.assertFalse((root / "save.dat.tmp").exists())

    def test_save_rejects_non_dict_payload(self):
        original_save_paths = (
            save._DATA_DIR,
            save.SAVE_FILE,
            save._LEGACY_APPDATA_JSON,
            save._LEGACY_CWD_JSON,
        )

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            save._DATA_DIR = root
            save.SAVE_FILE = str(root / "save.dat")
            save._LEGACY_APPDATA_JSON = str(root / "save.json")
            save._LEGACY_CWD_JSON = str(root / "cwd-save.json")

            try:
                self.assertFalse(save.save_game(["not", "a", "payload"]))
                self.assertFalse((root / "save.dat").exists())
            finally:
                (
                    save._DATA_DIR,
                    save.SAVE_FILE,
                    save._LEGACY_APPDATA_JSON,
                    save._LEGACY_CWD_JSON,
                ) = original_save_paths


if __name__ == "__main__":
    unittest.main()
