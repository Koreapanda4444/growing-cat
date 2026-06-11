import unittest
from unittest.mock import Mock, patch

from settings import SettingsScreen


class SettingsScreenTests(unittest.TestCase):
    def test_reset_data_does_not_restart_when_save_reset_fails(self):
        screen = object.__new__(SettingsScreen)
        screen.restart_callback = Mock()
        screen.running = True
        screen.message = ""

        with patch("settings.save.reset_save", return_value=False):
            self.assertFalse(SettingsScreen.reset_data(screen))

        screen.restart_callback.assert_not_called()
        self.assertTrue(screen.running)
        self.assertEqual(screen.message, "초기화 실패")


if __name__ == "__main__":
    unittest.main()
