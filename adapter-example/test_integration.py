"""Integration test: plain files and docstore documents joined in one document.

Needs a pdfannex checkout (package and CLI). Point PDFANNEX_HOME at it; the default is the
parent of this directory, which is right inside the pdfannex repository. Skipped if not found
or if texlua, pdflatex, pdftotext or curl are missing.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from docstore_server import DocstoreServer

HERE = Path(__file__).resolve().parent
HOME = Path(os.environ.get("PDFANNEX_HOME", HERE.parent))
CLI = HOME / "cli" / "pdfannex"
TEX = HOME / "tex"
NEEDS = (CLI.is_file() and TEX.is_dir()
         and all(shutil.which(t) for t in ("texlua", "pdflatex", "pdftotext", "curl")))

SRC = r"\documentclass{article}\pagestyle{empty}\begin{document}%s\end{document}"


def sh(cmd, cwd, check=True):
    env = {"PATH": os.environ["PATH"], "HOME": str(cwd), "TEXINPUTS": f"{TEX}:"}
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check, env=env)


def pdf(cwd, name, word):
    (Path(cwd) / f"{name}.tex").write_text(SRC % word)
    sh(["pdflatex", "-interaction=batchmode", f"{name}.tex"], cwd)


def tex(cwd, check=True):
    # No -halt-on-error: the first build reports unresolved URIs but still records every request.
    return sh(["pdflatex", "-interaction=nonstopmode", "host.tex"], cwd, check=check)


def text(cwd):
    return sh(["pdftotext", "host.pdf", "-"], cwd).stdout


DOC_HOST = r"""\documentclass{article}\usepackage{pdfannex}
\NewAnnexSource{\includedoc}{docstore}
\begin{document}
\includedoc[page-style=empty]{memo}{Memo}
\includeannex[page-style=empty]{pdfannex://docstore/memo?rev=1}{Old memo}
\includeannex[page-style=empty]{a.pdf}{Plain}
\end{document}
"""


@unittest.skipUnless(NEEDS, "pdfannex checkout or tools missing (set PDFANNEX_HOME)")
class PlainAndDocstore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.store = self.d / "store" / "memo"
        self.store.mkdir(parents=True)
        for rev, word in ((1, "FIRST"), (2, "SECOND")):
            pdf(self.d, f"r{rev}", word)
            (self.d / f"r{rev}.pdf").rename(self.store / f"{rev}.pdf")
        pdf(self.d, "a", "ALPHA")
        (self.d / "host.tex").write_text(DOC_HOST)
        self.server = DocstoreServer(self.d / "store", "tok").start()
        self.env = dict(os.environ, PATH=f"{HERE}:{os.environ['PATH']}",
                        PDFANNEX_DOCSTORE_URL=self.server.url, PDFANNEX_DOCSTORE_TOKEN="tok")
        self.run_cli("init")

    def tearDown(self):
        self.server.stop()
        self.tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run(["texlua", str(CLI), *args], cwd=self.d, env=self.env,
                              capture_output=True, text=True)

    def build(self):
        tex(self.d, check=False)

    def test_alias_pins_revisions_and_detects_updates(self):
        self.build()
        self.assertEqual(self.run_cli("prepare", "host.tex").returncode, 0)
        lock = json.loads((self.d / "pdfannex.lock").read_text())
        self.assertEqual(lock["sources"]["pdfannex://docstore/memo"]["resolved"],
                         "pdfannex://docstore/memo?rev=2")
        # The plain file is locked by the CLI itself, with no adapter involved.
        self.assertIn("pdfannex://file/a.pdf", lock["sources"])
        # A new revision and removed originals must not change the build.
        pdf(self.d, "r3", "THIRD")
        (self.d / "r3.pdf").rename(self.store / "3.pdf")
        status = self.run_cli("status", "host.tex").stdout
        self.assertIn("update-available pdfannex://docstore/memo\n", status)
        self.assertIn("up-to-date", status)
        shutil.rmtree(self.store)
        (self.d / "a.pdf").unlink()
        for aux in ("host.aux", "host.pdf"):
            (self.d / aux).unlink(missing_ok=True)
        self.build()
        out = text(self.d)
        for word in ("SECOND", "FIRST", "ALPHA"):
            self.assertIn(word, out)
        self.assertLess(out.index("SECOND"), out.index("FIRST"))
        self.assertLess(out.index("FIRST"), out.index("ALPHA"))
        self.assertNotIn("THIRD", out)

    def test_tampered_revision_is_rejected_by_the_cli(self):
        self.build()
        self.run_cli("prepare", "host.tex")
        shutil.rmtree(self.d / ".pdfannex/objects")
        pdf(self.d, "evil", "EVIL")
        (self.d / "evil.pdf").replace(self.store / "2.pdf")
        run = self.run_cli("prepare", "host.tex")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("hash mismatch", run.stderr)

    def test_locked_build_needs_neither_resolver_nor_server(self):
        self.build()
        self.run_cli("prepare", "host.tex")
        self.server.stop()
        self.env["PATH"] = os.environ["PATH"]
        run = self.run_cli("prepare", "host.tex")
        self.assertEqual(run.returncode, 0, run.stderr)
        (self.d / "a.pdf").unlink()
        (self.d / "host.aux").unlink(missing_ok=True)
        self.build()
        self.assertIn("SECOND", text(self.d))
        self.server = DocstoreServer(self.d / "store", "tok").start()  # for tearDown

    def test_outage_and_bad_credentials_keep_the_lock(self):
        self.build()
        self.run_cli("prepare", "host.tex")
        lock = (self.d / "pdfannex.lock").read_text()
        shutil.rmtree(self.d / ".pdfannex/objects")
        self.env["PDFANNEX_DOCSTORE_TOKEN"] = "wrong"
        run = self.run_cli("prepare", "host.tex")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("authentication-required", run.stderr)
        self.server.force_status = 503
        self.env["PDFANNEX_DOCSTORE_TOKEN"] = "tok"
        run = self.run_cli("update", "host.tex")
        self.assertIn("temporarily-unavailable", run.stderr)
        self.assertEqual((self.d / "pdfannex.lock").read_text(), lock)

    def test_missing_curl_recommends_installing_it_and_updating_path(self):
        self.build()
        bin_dir = self.d / "without-curl"
        bin_dir.mkdir()
        for name in ("texlua",):
            (bin_dir / name).symlink_to(shutil.which(name))
        (bin_dir / "pdfannex-resolver-docstore").symlink_to(HERE / "pdfannex-resolver-docstore")
        (bin_dir / "adapter-lib.lua").symlink_to(HERE / "adapter-lib.lua")
        self.env["PATH"] = str(bin_dir)

        run = self.run_cli("prepare", "host.tex")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("install curl", run.stderr)
        self.assertIn("PATH", run.stderr)

    def test_unknown_option_and_missing_document(self):
        for src in ("pdfannex://docstore/memo?x=1", "pdfannex://docstore/none"):
            (self.d / "host.pdfannex-requests").write_text(src.encode().hex().upper() + "\n")
            run = self.run_cli("prepare", "host.tex")
            self.assertNotEqual(run.returncode, 0, src)


if __name__ == "__main__":
    unittest.main()
