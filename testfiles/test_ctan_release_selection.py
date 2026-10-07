import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".github" / "scripts"))

from ctan_release_selection import eligible_release_tags, normalize_version


class ReleaseSelectionTests(unittest.TestCase):
    def test_normalize_version_removes_release_please_marker(self):
        self.assertEqual(
            normalize_version("0.6.2 # x-release-please-version\n"),
            "0.6.2",
        )

    def test_only_published_matching_semver_releases_are_eligible(self):
        releases = [
            {
                "tag_name": "pdfannex-v0.6.1",
                "draft": False,
                "prerelease": False,
                "published_at": "2026-10-06T14:00:00Z",
            },
            {
                "tag_name": "pdfannex-v0.6.2",
                "draft": False,
                "prerelease": False,
                "published_at": "2026-10-07T16:00:00Z",
            },
            {
                "tag_name": "pdfannex-v0.7.0",
                "draft": True,
                "prerelease": False,
                "published_at": "2026-10-08T16:00:00Z",
            },
            {
                "tag_name": "pdfannex-v0.8.0",
                "draft": False,
                "prerelease": True,
                "published_at": "2026-10-09T16:00:00Z",
            },
            {
                "tag_name": "not-a-release",
                "draft": False,
                "prerelease": False,
                "published_at": "2026-10-10T16:00:00Z",
            },
            {
                "tag_name": "pdfannex-v0.6.3",
                "draft": False,
                "prerelease": False,
                "published_at": "2026-10-11T16:00:00Z",
            },
        ]
        versions = {
            "pdfannex-v0.6.1": "0.6.1",
            "pdfannex-v0.6.2": "0.6.2",
            "pdfannex-v0.6.3": "0.6.2",
        }

        result = eligible_release_tags(releases, versions.__getitem__)

        self.assertEqual(result, ["pdfannex-v0.6.2", "pdfannex-v0.6.1"])


if __name__ == "__main__":
    unittest.main()
