import json
import tempfile
import unittest
from pathlib import Path

from library_cleaner.settings import load_settings, save_settings


class LibraryCleanerSettingsTests(unittest.TestCase):
    def test_saves_and_loads_sqlite_path(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "settings.json"
            sqlite_path = r"D:\RadioBOSS\tracks.db"
            self.assertTrue(save_settings({"sqlite_path": sqlite_path}, target))
            self.assertEqual(load_settings(target)["sqlite_path"], sqlite_path)

    def test_missing_or_invalid_settings_return_empty_dictionary(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "settings.json"
            self.assertEqual(load_settings(target), {})
            target.write_text("not json", encoding="utf-8")
            self.assertEqual(load_settings(target), {})

    def test_only_sqlite_path_is_saved(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "settings.json"
            self.assertTrue(save_settings({
                "sqlite_path": "C:/tracks.db",
                "password": "must-not-be-saved",
            }, target))
            stored = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(stored, {"sqlite_path": "C:/tracks.db"})


if __name__ == "__main__":
    unittest.main()
