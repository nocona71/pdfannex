import hashlib
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / ".github" / "scripts" / "ctan_submission_preview.lua"


class SubmissionPreviewTests(unittest.TestCase):
    def run_preview(self, announcement, email="ctan-test@example.invalid"):
        with tempfile.TemporaryDirectory() as temporary_directory:
            archive = Path(temporary_directory) / "pdfannex-ctan-v0.6.2.zip"
            announcement_file = Path(temporary_directory) / "announcement.txt"
            archive.write_bytes(b"test archive")
            announcement_file.write_text(announcement, encoding="utf-8")
            checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
            environment = os.environ.copy()
            environment.pop("CTAN_EMAIL", None)
            if email is not None:
                environment["CTAN_EMAIL"] = email

            return subprocess.run(
                [
                    "texlua",
                    str(PREVIEW),
                    "0.6.2",
                    str(archive),
                    str(announcement_file),
                    checksum,
                ],
                cwd=ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )

    def test_preview_uses_metadata_and_hides_uploader_email(self):
        result = self.run_preview("Release <b>notes</b>")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Version:** `0.6.2`", result.stdout)
        self.assertIn("Author:** Toni Incog", result.stdout)
        self.assertIn("Uploader email:** configured (redacted)", result.stdout)
        self.assertNotIn("ctan-test@example.invalid", result.stdout)
        self.assertIn("Release &lt;b&gt;notes&lt;/b&gt;", result.stdout)

    def test_preview_rejects_missing_email(self):
        result = self.run_preview("Release notes", email=None)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CTAN_EMAIL", result.stderr)

    def test_preview_rejects_empty_or_oversized_announcement(self):
        empty = self.run_preview("  \n")
        oversized = self.run_preview("x" * 8193)

        self.assertNotEqual(empty.returncode, 0)
        self.assertIn("announcement is empty", empty.stderr)
        self.assertNotEqual(oversized.returncode, 0)
        self.assertIn("8192-byte limit", oversized.stderr)


if __name__ == "__main__":
    unittest.main()
