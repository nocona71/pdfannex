"""End-to-end tests of local file inclusion and the optional CLI."""

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
LATEX_ENGINES = ("pdflatex", "xelatex", "lualatex")
PLAIN_NEEDS = shutil.which("pdftotext") and all(shutil.which(engine) for engine in LATEX_ENGINES)
LOCAL_NAMES = (
    "sub dir/Steuerbescheid 2025 \u00dc.pdf",
    "100%.pdf",
    "a&b#c_d.pdf",
    "x?y=1.pdf",
    "-option.pdf",
    "literal%41.pdf",
)

SRC = r"\documentclass{article}\pagestyle{empty}\begin{document}%s\end{document}"
HOST = r"""\documentclass{article}\usepackage{pdfannex}
\begin{document}
\includeannex[page-style=empty]{%s}{Doc}
\end{document}
"""


def sh(cmd, cwd, check=True, env=None, **kw):
    run_env = os.environ.copy()
    run_env.update({"HOME": str(cwd), "TEXINPUTS": f"{ROOT / 'tex'}{os.pathsep}"})
    if env:
        run_env.update(env)
    try:
        return subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, check=check, env=run_env, **kw
        )
    except subprocess.CalledProcessError as exc:
        raise AssertionError(
            f"command failed ({exc.returncode}): {cmd!r}\n"
            f"stdout:\n{exc.stdout}\nstderr:\n{exc.stderr}"
        ) from exc


def pdf(cwd, name, text):
    (Path(cwd) / f"{name}.tex").write_text(SRC % text)
    sh(["pdflatex", "-interaction=batchmode", f"{name}.tex"], cwd)


def tex_file_argument(name):
    return name.replace("%", r"\%").replace("#", r"\#").replace("&", r"\&").replace("_", r"\_")


def latex(cwd, source="a.pdf"):
    (Path(cwd) / "host.tex").write_text(HOST % source)
    return sh(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "host.tex"], cwd, check=False)


def write_requests(cwd, *sources):
    (Path(cwd) / "host.pdfannex-requests").write_text(
        "".join(s.encode().hex().upper() + "\n" for s in sources))


def cli(cwd, *args, check=True, env=None):
    return sh(["texlua", str(CLI), *args], cwd, check=check, env=env)


def text(cwd):
    return sh(["pdftotext", "host.pdf", "-"], cwd).stdout


@unittest.skipUnless(PLAIN_NEEDS, "pdflatex/xelatex/lualatex/pdftotext missing")
class PlainLocalFileNames(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        includes = []
        for i, name in enumerate(LOCAL_NAMES):
            pdf(self.d, f"source{i}", f"NAME{i}")
            path = self.d / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(self.d / f"source{i}.pdf", path)
            includes.append(
                r"\includeannex[page-style=empty]{%s}{N%d}" % (tex_file_argument(name), i)
            )
        (self.d / "host.tex").write_text(
            r"\documentclass{article}\usepackage[utf8]{inputenc}\usepackage{pdfannex}"
            r"\pagestyle{empty}\begin{document}" + "".join(includes) + r"\end{document}"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_local_names_are_literal_across_engines_without_the_cli(self):
        for engine in LATEX_ENGINES:
            with self.subTest(engine=engine):
                run = sh(
                    [engine, "-interaction=nonstopmode", "-halt-on-error", "host.tex"],
                    self.d,
                    check=False,
                )
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                output = text(self.d)
                for i in range(len(LOCAL_NAMES)):
                    self.assertIn(f"NAME{i}", output)
                self.assertFalse((self.d / "host.pdfannex-requests").exists())


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
        cases = [("../x.pdf", "permission-denied"),
                 ("/etc/passwd", "invalid-source"),
                 ("pdfannex://file/a.pdf?rev=2", "unsupported-source-option"),
                 ("missing.pdf", "resource-not-found")]
        try:
            target = self.d / "target.pdf"
            target.write_bytes(b"")
            os.symlink(target, self.d / "link.pdf")
            cases.append(("link.pdf", "permission-denied"))
        except (NotImplementedError, OSError):
            pass
        for src, code in cases:
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
            tex_file_argument(n), i) for i, n in enumerate(names))
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


@unittest.skipUnless(shutil.which("texlua"), "texlua missing")
class CliProcess(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.project = self.d / "project dir"
        self.project.mkdir()
        cli(self.project, "init")

    def tearDown(self):
        self.tmp.cleanup()

    def test_file_source_with_path_spaces(self):
        shutil.copy(ROOT / "testfiles" / "support" / "a1.pdf", self.project / "a1.pdf")
        write_requests(self.project, "a1.pdf")
        doc = str(Path("project dir") / "host.tex")
        run = cli(self.d, "prepare", doc)
        self.assertIn("1 source(s) locked", run.stdout)
        self.assertTrue((self.project / "pdfannex.lock").exists())

    def test_missing_resolver_reports_on_stderr(self):
        write_requests(self.project, "pdfannex://nowhere/1")
        run = cli(self.project, "prepare", "host.tex", check=False)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("no resolver 'pdfannex-resolver-nowhere'", run.stderr)
        self.assertEqual(run.stdout, "")

    @unittest.skipUnless(os.name == "nt", "Windows drive paths only")
    def test_drive_path_is_not_a_project_relative_file(self):
        write_requests(self.project, "C:/Windows/win.ini")
        run = cli(self.project, "prepare", "host.tex", check=False)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("invalid-source", run.stderr)

    def test_resolver_script_on_path_runs_through_texlua(self):
        resolver_dir = self.d / "resolver %PATH% scripts"
        resolver_dir.mkdir()
        resolver = resolver_dir / "pdfannex-resolver-mock"
        resolver.write_text(
            'local request = io.stdin:read("a")\n'
            'if request:find(\'"operation":"describe"\', 1, true) then\n'
            '  io.write(\'{"protocolVersions":[1],"schemes":["mock"],"capabilities":["resolve"]}\')\n'
            'else\n'
            '  local path = assert(os.getenv("PDFANNEX_TEST_PDF"))\n'
            '  path = path:gsub("\\\\", "\\\\\\\\"):gsub(\'"\', \'\\\\"\')\n'
            '  io.write(\'{"protocolVersion":1,"results":[{"id":"pdfannex://mock/1",\' ..\n'
            '    \'"resolved":"pdfannex://mock/1","artifact":{"path":"\' .. path .. \'"}}]}\')\n'
            'end\n'
        )
        write_requests(self.project, "pdfannex://mock/1")
        env = {
            "PATH": str(resolver_dir) + os.pathsep + os.environ["PATH"],
            "PDFANNEX_TEST_PDF": str(ROOT / "testfiles" / "support" / "a1.pdf"),
        }
        run = cli(self.project, "prepare", "host.tex", env=env)
        self.assertIn("1 source(s) locked", run.stdout)


if __name__ == "__main__":
    unittest.main()
