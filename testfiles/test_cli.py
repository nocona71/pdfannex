"""End-to-end tests of the pdfannex CLI (built-in file handling)."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

CLI = ROOT / "cli" / "pdfannex"
NEEDS = shutil.which("texlua") and shutil.which("pdflatex") and shutil.which("pdftotext")

SRC = r"\documentclass{article}\pagestyle{empty}\begin{document}%s\end{document}"
HOST = r"""\documentclass{article}\usepackage{pdfannex}
\begin{document}
\includeannex[page-style=empty]{%s}{Doc}
\end{document}
"""


def sh(cmd, cwd, check=True, **kw):
    env = {"PATH": os.environ["PATH"], "HOME": str(cwd), "TEXINPUTS": f"{ROOT / 'tex'}:"}
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check, env=env, **kw)


def pdf(cwd, name, text):
    (Path(cwd) / f"{name}.tex").write_text(SRC % text)
    sh(["pdflatex", "-interaction=batchmode", f"{name}.tex"], cwd)


def latex(cwd, source="a.pdf"):
    (Path(cwd) / "host.tex").write_text(HOST % source)
    return sh(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "host.tex"], cwd, check=False)


def write_requests(cwd, *sources):
    (Path(cwd) / "host.pdfannex-requests").write_text(
        "".join(s.encode().hex().upper() + "\n" for s in sources))


def cli(cwd, *args, check=True):
    return sh(["texlua", str(CLI), *args], cwd, check=check)


def text(cwd):
    return sh(["pdftotext", "host.pdf", "-"], cwd).stdout


@unittest.skipUnless(NEEDS, "texlua/pdflatex/pdftotext missing")
class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        pdf(self.d, "a", "ALPHA")
        pdf(self.d, "b", "BETA")
        cli(self.d, "init")

    def tearDown(self):
        self.tmp.cleanup()

    def lock(self):
        latex(self.d)
        return cli(self.d, "prepare", "host.tex")

    def test_files_are_confined_to_the_project(self):
        (self.d / "sub").mkdir()
        os.symlink("/etc/hostname", self.d / "link.pdf")
        for src, code in [("../x.pdf", "permission-denied"),
                          ("/etc/passwd", "invalid-source"),
                          ("link.pdf", "permission-denied"),
                          ("pdfannex://file/a.pdf?rev=2", "unsupported-source-option"),
                          ("missing.pdf", "resource-not-found")]:
            write_requests(self.d, src)
            run = cli(self.d, "prepare", "host.tex", check=False)
            self.assertNotEqual(run.returncode, 0, src)
            self.assertIn(code, run.stderr, src)
            self.assertFalse((self.d / "pdfannex.lock").read_text().count("passwd"), src)

    def test_lock_store_and_rebuild(self):
        self.assertIn("1 source(s) locked", self.lock().stdout)
        lock = json.loads((self.d / "pdfannex.lock").read_text())
        entry = lock["sources"]["pdfannex://file/a.pdf"]
        self.assertTrue((self.d / ".pdfannex/objects/sha256" / entry["sha256"][:2]
                         / f"{entry['sha256']}.pdf").exists())
        self.assertEqual(entry["resolver"], "file")
        self.assertEqual(latex(self.d).returncode, 0)
        self.assertIn("ALPHA", text(self.d))
        cli(self.d, "verify", "host.tex")

    def test_build_ignores_changed_source_until_update(self):
        self.lock()
        shutil.copy(self.d / "b.pdf", self.d / "a.pdf")
        latex(self.d)
        self.assertIn("ALPHA", text(self.d))
        self.assertIn("update-available", cli(self.d, "status", "host.tex").stdout)
        self.assertEqual(cli(self.d, "prepare", "host.tex").returncode, 0)  # fast path
        self.assertIn("ALPHA", text(self.d))
        cli(self.d, "update", "host.tex")
        latex(self.d)
        self.assertIn("BETA", text(self.d))
        self.assertIn("up-to-date", cli(self.d, "status", "host.tex").stdout)

    def test_exact_recovery_and_hash_mismatch(self):
        self.lock()
        shutil.rmtree(self.d / ".pdfannex/objects")
        self.assertEqual(cli(self.d, "prepare", "host.tex").returncode, 0)
        shutil.rmtree(self.d / ".pdfannex/objects")
        shutil.copy(self.d / "b.pdf", self.d / "a.pdf")
        run = cli(self.d, "prepare", "host.tex", check=False)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("hash mismatch", run.stderr)

    def test_corrupt_store_fails_verify(self):
        self.lock()
        obj = next((self.d / ".pdfannex/objects").rglob("*.pdf"))
        obj.write_bytes(obj.read_bytes() + b"tamper")
        run = cli(self.d, "verify", "host.tex", check=False)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("hash does not match", run.stderr)

    def test_failed_batch_keeps_old_lock(self):
        self.lock()
        before = (self.d / "pdfannex.lock").read_text()
        write_requests(self.d, "a.pdf", "missing.pdf")
        run = cli(self.d, "update", "host.tex", check=False)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("resource-not-found", run.stderr)
        self.assertEqual((self.d / "pdfannex.lock").read_text(), before)

    def test_unusual_file_names(self):
        (self.d / "sub dir").mkdir()
        names = ["sub dir/Steuerbescheid 2025 \u00dc.pdf", "100%.pdf", "a&b#c_d.pdf", "x?y=1.pdf"]
        for i, name in enumerate(names):
            pdf(self.d, f"n{i}", f"NAME{i}")
            shutil.move(self.d / f"n{i}.pdf", self.d / name)
        tex = "".join(r"\includeannex[page-style=empty]{%s}{N%d}" % (
            n.replace("%", r"\%").replace("#", r"\#").replace("&", r"\&").replace("_", r"\_"), i) for i, n in enumerate(names))
        (self.d / "host.tex").write_text(
            r"\documentclass{article}\usepackage[utf8]{inputenc}\usepackage{pdfannex}"
            r"\begin{document}" + tex + r"\end{document}")
        build = lambda eng: sh([eng, "-interaction=nonstopmode", "-halt-on-error", "host.tex"],
                               self.d, check=False)
        build("pdflatex")
        cli(self.d, "prepare", "host.tex")
        for n in names:
            (self.d / n).unlink()   # only the store can satisfy the build now
        for engine in ("pdflatex", "xelatex", "lualatex"):
            with self.subTest(engine=engine):
                (self.d / "host.pdfannex-requests").unlink()
                self.assertEqual(build(engine).returncode, 0)
                out = text(self.d)
                for i in range(len(names)):
                    self.assertIn(f"NAME{i}", out)
                # Every engine must write the same requests the CLI locked.
                cli(self.d, "verify", "host.tex")

    def test_requests_are_opt_in(self):
        (self.d / "pdfannex.lock").unlink()
        latex(self.d)
        self.assertFalse((self.d / "host.pdfannex-requests").exists())
        cli(self.d, "init")
        self.assertIn("already exists", cli(self.d, "init").stdout)
        latex(self.d)
        self.assertTrue((self.d / "host.pdfannex-requests").exists())
        self.assertIn("1 source(s) locked", cli(self.d, "prepare", "host.tex").stdout)

    def test_non_pdf_is_rejected(self):
        (self.d / "a.pdf").write_text("not a pdf")
        latex(self.d)
        run = cli(self.d, "prepare", "host.tex", check=False)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("not a PDF", run.stderr)

    def test_unknown_scheme_needs_a_resolver(self):
        latex(self.d)
        write_requests(self.d, "pdfannex://nowhere/1")
        run = cli(self.d, "prepare", "host.tex", check=False)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("pdfannex-resolver-nowhere", run.stderr)

    def test_unresolved_uri_source_is_a_latex_error(self):
        run = latex(self.d, "pdfannex://paperless/1")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("is not resolved", run.stdout)


if __name__ == "__main__":
    unittest.main()
