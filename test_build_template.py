import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import build_template


ROOT = Path(__file__).resolve().parent


class CleanTemplateTests(unittest.TestCase):
    def test_template_contains_manifest_files_and_no_runtime_state(self):
        manifest = build_template.load_manifest()
        expected = {
            path.as_posix()
            for path in (
                set(manifest["managed_files"]) | set(manifest["seed_if_missing"])
            )
        }

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "template"
            files = build_template.build_directory(output)
            actual = {
                path.relative_to(output).as_posix()
                for path in output.rglob("*")
                if path.is_file()
            }

        self.assertEqual(actual, expected)
        self.assertEqual({path.as_posix() for path in files}, expected)
        self.assertNotIn("data/state.json", actual)
        self.assertNotIn("data/kakao_auth.json", actual)
        self.assertNotIn("TASK.md", actual)
        self.assertNotIn("CHECKPOINT.md", actual)
        self.assertIn("user_config.json", actual)
        self.assertIn("PTIS_VERSION", actual)

    def test_default_user_config_is_safe_and_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "template"
            build_template.build_directory(output)
            payload = json.loads(
                (output / "user_config.json").read_text(encoding="utf-8")
            )

        self.assertEqual(payload, build_template.DEFAULT_USER_CONFIG)
        self.assertFalse(payload["focus_search"]["enabled"])
        self.assertFalse(payload["route_watch"]["enabled"])

    def test_repeated_zip_build_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            first_dir = base / "first"
            second_dir = base / "second"
            first_zip = base / "first.zip"
            second_zip = base / "second.zip"

            build_template.build_directory(first_dir)
            build_template.build_zip(first_dir, first_zip)
            build_template.build_directory(second_dir)
            build_template.build_zip(second_dir, second_zip)

            self.assertEqual(
                hashlib.sha256(first_zip.read_bytes()).hexdigest(),
                hashlib.sha256(second_zip.read_bytes()).hexdigest(),
            )

            with zipfile.ZipFile(first_zip) as archive:
                names = set(archive.namelist())
            self.assertNotIn("data/state.json", names)
            self.assertNotIn("data/kakao_auth.json", names)

    def test_output_inside_source_repository_is_rejected(self):
        with self.assertRaises(build_template.TemplateBuildError):
            build_template.build_directory(ROOT / "_template_output_forbidden")


if __name__ == "__main__":
    unittest.main()
