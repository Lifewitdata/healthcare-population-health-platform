import os
import unittest
from unittest.mock import patch
from healthcare.auth import PASSWORD_ENV, login_password, password_options


class PasswordTests(unittest.TestCase):
    def test_prompt_shared_and_cleaned_on_error(self):
        with patch.dict(os.environ, {"SNOWFLAKE_AUTHENTICATOR": "snowflake"}, clear=True):
            with patch("healthcare.auth.getpass.getpass", return_value="test-only"):
                with self.assertRaises(RuntimeError):
                    with login_password(True):
                        self.assertEqual(password_options(), {"password": "test-only"})
                        self.assertEqual(os.environ[PASSWORD_ENV], "test-only")
                        raise RuntimeError("failed build")
            self.assertNotIn(PASSWORD_ENV, os.environ)

    def test_supplied_secret_preserved(self):
        with patch.dict(os.environ, {"SNOWFLAKE_AUTHENTICATOR": "snowflake", PASSWORD_ENV: "test-only"}, clear=True):
            with patch("healthcare.auth.getpass.getpass") as prompt:
                with login_password(True):
                    self.assertEqual(password_options()["password"], "test-only")
                prompt.assert_not_called()
            self.assertEqual(os.environ[PASSWORD_ENV], "test-only")

    def test_browser_and_local_do_not_prompt(self):
        for enabled, auth in [(True, "externalbrowser"), (False, "snowflake")]:
            with patch.dict(os.environ, {"SNOWFLAKE_AUTHENTICATOR": auth}, clear=True):
                with patch("healthcare.auth.getpass.getpass") as prompt:
                    with login_password(enabled):
                        pass
                    prompt.assert_not_called()

    def test_missing_password_rejected(self):
        with patch.dict(os.environ, {"SNOWFLAKE_AUTHENTICATOR": "snowflake"}, clear=True):
            with self.assertRaises(ValueError):
                password_options()
