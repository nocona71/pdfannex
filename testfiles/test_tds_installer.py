"""Test safe installation and removal of TDS archives in a user tree."""

import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/install-texmfhome-tds.sh"


class TdsInstaller(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.work = Path(self.temporary.name)
        self.texmfhome = self.work / "texmf"
        self.bin = self.work / "bin"
        self.bin.mkdir()
        self.mktexlsr_log = self.work / "mktexlsr.log"
        mktexlsr = self.bin / "mktexlsr"
        mktexlsr.write_text(
            "#!/usr/bin/env bash\nprintf '%s\\n' \"$1\" >> \"$MKTXLSR_LOG\"\n",
            encoding="utf-8",
        )
        mktexlsr.chmod(0o755)
        self.env = dict(
            os.environ,
            PATH=f"{self.bin}:{os.environ['PATH']}",
            MKTXLSR_LOG=str(self.mktexlsr_log),
        )
        self.archive = self.work / "pdfannex.tds.zip"
        with zipfile.ZipFile(self.archive, "w") as package:
            self.add_file(package, "tex/latex/pdfannex/pdfannex.sty", b"package")
            self.add_file(
                package,
                "scripts/pdfannex/pdfannex",
                b"#!/usr/bin/env texlua\n",
                0o755,
            )

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def add_file(package, name, data, mode=0o644):
        info = zipfile.ZipInfo(name)
        info.external_attr = (stat.S_IFREG | mode) << 16
        package.writestr(info, data)

    def run_installer(self, *args):
        return subprocess.run(
            ["bash", str(INSTALLER), *map(str, args), str(self.texmfhome)],
            env=self.env,
            capture_output=True,
            text=True,
        )

    def test_install_and_uninstall_only_owned_files(self):
        installed = self.run_installer("install", self.archive)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        style = self.texmfhome / "tex/latex/pdfannex/pdfannex.sty"
        cli = self.texmfhome / "scripts/pdfannex/pdfannex"
        self.assertEqual(style.read_bytes(), b"package")
        self.assertTrue(cli.stat().st_mode & stat.S_IXUSR)
        unrelated = self.texmfhome / "unrelated.txt"
        unrelated.write_text("keep", encoding="utf-8")

        removed = self.run_installer("uninstall", "pdfannex")
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse(style.exists())
        self.assertFalse(cli.exists())
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep")
        self.assertFalse((self.texmfhome / ".pdfannex-tds-manifests").exists())
        self.assertEqual(len(self.mktexlsr_log.read_text().splitlines()), 2)

    def test_install_refuses_to_overwrite_existing_files(self):
        style = self.texmfhome / "tex/latex/pdfannex/pdfannex.sty"
        style.parent.mkdir(parents=True)
        style.write_text("user file", encoding="utf-8")

        result = self.run_installer("install", self.archive)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to overwrite", result.stderr)
        self.assertEqual(style.read_text(encoding="utf-8"), "user file")
        self.assertFalse((self.texmfhome / "scripts/pdfannex/pdfannex").exists())

    def test_install_rejects_archive_path_traversal(self):
        archive = self.work / "unsafe.tds.zip"
        with zipfile.ZipFile(archive, "w") as package:
            self.add_file(package, "../outside.txt", b"unsafe")

        result = self.run_installer("install", archive)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe archive path", result.stderr)
        self.assertFalse((self.work / "outside.txt").exists())

    def test_install_rejects_symbolic_links(self):
        archive = self.work / "symlink.tds.zip"
        with zipfile.ZipFile(archive, "w") as package:
            info = zipfile.ZipInfo("link")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            package.writestr(info, "../outside")

        result = self.run_installer("install", archive)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symbolic links are not allowed", result.stderr)
        self.assertFalse((self.texmfhome / "link").exists())

    def test_install_refuses_symlinked_manifest_directory(self):
        outside = self.work / "outside"
        outside.mkdir()
        self.texmfhome.mkdir()
        (self.texmfhome / ".pdfannex-tds-manifests").symlink_to(outside)

        result = self.run_installer("install", self.archive)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked manifest directory", result.stderr)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.texmfhome / "tex/latex/pdfannex/pdfannex.sty").exists())


if __name__ == "__main__":
    unittest.main()
