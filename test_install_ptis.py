import subprocess
import unittest
from unittest.mock import patch

import install_ptis


class RepositorySlugTests(unittest.TestCase):
    def test_https_remote(self):
        self.assertEqual(
            install_ptis._parse_repository_slug(
                "https://github.com/example/flight-bot.git"
            ),
            "example/flight-bot",
        )

    def test_ssh_remote(self):
        self.assertEqual(
            install_ptis._parse_repository_slug("git@github.com:example/flight-bot.git"),
            "example/flight-bot",
        )

    def test_non_github_remote_is_rejected(self):
        with self.assertRaises(install_ptis.InstallError):
            install_ptis._parse_repository_slug("https://example.com/repo.git")


class SecretTests(unittest.TestCase):
    @patch("install_ptis._run")
    def test_secret_value_is_sent_on_stdin(self, run):
        install_ptis._set_repository_secret("example/flight-bot", "TOKEN", "secret")
        run.assert_called_once_with(
            ["gh", "secret", "set", "TOKEN", "--repo", "example/flight-bot"],
            input_text="secret",
        )

    @patch("install_ptis._run")
    def test_dirty_worktree_is_rejected(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, stdout=" M main.py\n")
        with self.assertRaises(install_ptis.InstallError):
            install_ptis._require_clean_worktree()


if __name__ == "__main__":
    unittest.main()
