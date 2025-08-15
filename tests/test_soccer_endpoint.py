import unittest
from unittest.mock import patch
import sys
import os

# Ensure parent folder is on sys.path so imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import utah_state_notifier

class TestUtahStateNotifier(unittest.TestCase):

    @patch("utah_state_notifier.send_push_notification")
    @patch("utah_state_notifier.fetch_games")
    def test_utah_state_win_detected(self, mock_fetch_games, mock_send_push):
        # Mock API returns a single Utah State win
        mock_fetch_games.return_value = [
            {
                "game": {
                    "status": {"state": "final"},
                    "home": {"names": {"short": "Washington St."}, "score": "0"},
                    "away": {"names": {"short": "Utah St."}, "score": "1"},
                    "title": "Washington St. vs Utah St."
                }
            }
        ]

        # Limit SPORTS to a single sport for this test
        with patch.object(utah_state_notifier, "SPORTS", {
            "soccer-women": {"division": "d1", "conference": "mountain-west"}
        }):
            utah_state_notifier.check_sports_for_wins()

        # Assert the push was called exactly once
        mock_send_push.assert_called_once_with("🎉 Utah State won! Washington St. vs Utah St.")

    @patch("utah_state_notifier.send_push_notification")
    @patch("utah_state_notifier.fetch_games")
    def test_no_notification_for_loss(self, mock_fetch_games, mock_send_push):
        # Mock API returns a Utah State loss
        mock_fetch_games.return_value = [
            {
                "game": {
                    "status": {"state": "final"},
                    "home": {"names": {"short": "Utah St."}, "score": "0"},
                    "away": {"names": {"short": "Washington St."}, "score": "1"},
                    "title": "Utah St. vs Washington St."
                }
            }
        ]

        # Limit SPORTS to a single sport for this test
        with patch.object(utah_state_notifier, "SPORTS", {
            "soccer-women": {"division": "d1", "conference": "mountain-west"}
        }):
            utah_state_notifier.check_sports_for_wins()

        # Assert the push was not called
        mock_send_push.assert_not_called()

if __name__ == "__main__":
    unittest.main()
