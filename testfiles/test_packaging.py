"""Validate version metadata and the CTAN archive layout."""

from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = r"([0-9]+\.[0-9]+\.[0-9]+)"


class Packaging(unittest.TestCase):
    def test_versions_agree(self):
        version = re.fullmatch(
            VERSION_RE + r"\s+# x-release-please-version",
            (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        )
        self.assertIsNotNone(version)
        v = version.group(1)
        style = (ROOT / "tex/pdfannex.sty").read_text(encoding="utf-8")
        m = re.search(
            r"\\ProvidesPackage\{pdfannex\}\[\d{4}/\d{2}/\d{2} v"
            + VERSION_RE + r" ", style)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), v)
        self.assertIn("github.com/nocona71/pdfannex/issues", style)
        doc = (ROOT / "doc/pdfannex-doc.tex").read_text(encoding="utf-8")
        self.assertIn(f"\\date{{Version {v}}}", doc)
        manifest = (ROOT / ".release-please-manifest.json").read_text()
        self.assertIn(f'"{v}"', manifest)

    @unittest.skipUnless(shutil.which("texlua"), "texlua not available")
    def test_cli_reports_package_version(self):
        style = (ROOT / "tex/pdfannex.sty").read_text(encoding="utf-8")
        match = re.search(
            r"\\ProvidesPackage\{pdfannex\}\[\d{4}/\d{2}/\d{2} v"
            + VERSION_RE + r" ", style)
        self.assertIsNotNone(match)
        assert match is not None
        result = subprocess.run(
            ["texlua", str(ROOT / "cli/pdfannex"), "--version"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), f"pdfannex {match.group(1)}")

    def test_release_workflow_tag_prefix(self):
        text = (ROOT / ".github/workflows/ctan-release.yml").read_text()
        self.assertNotIn("paperless", text)
        self.assertIn("pdfannex-v", text)

    @unittest.skipUnless(shutil.which("l3build"), "l3build not available")
    def test_ctan_archive(self):
        with tempfile.TemporaryDirectory() as d:
            project = Path(d) / "project"
            project.mkdir()
            for name in ("build.lua", "tex", "doc", "testfiles", "cli",
                         "README.md", "CHANGELOG.md", "LICENSE", "VERSION"):
                src = ROOT / name
                if src.is_dir():
                    shutil.copytree(src, project / name)
                else:
                    shutil.copy2(src, project / name)
            r = subprocess.run(["l3build", "ctan"], cwd=project,
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            names = set(zipfile.ZipFile(project / "pdfannex-ctan.zip").namelist())
            for n in ("pdfannex/pdfannex.sty", "pdfannex/README.md",
                      "pdfannex/CHANGELOG.md", "pdfannex/LICENSE",
                      "pdfannex/pdfannex-doc.tex", "pdfannex/pdfannex-doc.pdf",
                      "pdfannex/scripts/pdfannex/pdfannex",
                      "pdfannex/scripts/pdfannex/pdfannex-lib.lua",
                      "pdfannex/pdfannex.1"):
                self.assertIn(n, names)
            tds = set(zipfile.ZipFile(
                project / "build/distrib/tds/pdfannex.tds.zip").namelist())
            self.assertIn("tex/latex/pdfannex/pdfannex.sty", tds)
            self.assertIn("scripts/pdfannex/pdfannex", tds)
            self.assertIn("scripts/pdfannex/pdfannex-lib.lua", tds)
            self.assertIn("doc/man/man1/pdfannex.1", tds)
            self.assertIn("doc/latex/pdfannex/pdfannex-doc.pdf", tds)


if __name__ == "__main__":
    unittest.main()
