"""Build and exercise the standalone CTAN/TDS package installation."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import zipfile

from docstore_server import DocstoreServer

HERE = Path(__file__).resolve().parent
CORE = Path(os.environ.get("PDFANNEX_HOME", HERE.parent)).resolve()
CORE_CLI = CORE / "cli" / "pdfannex"
CORE_TEX = CORE / "tex" / "pdfannex.sty"
BUILD_INPUTS = (
    "build.lua",
    "Makefile",
    "pdfannex-docstore.sty",
    "pdfannex-resolver-docstore",
    "adapter-lib.lua",
    "scripts",
    "ctan",
)
CORE_BUILD_INPUTS = (
    "build.lua",
    "tex",
    "cli",
    "doc",
    "testfiles",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "VERSION",
)
CAN_PACKAGE = shutil.which("l3build")
CAN_INSTALL_TEST = (
    CAN_PACKAGE
    and all(
        shutil.which(tool)
        for tool in ("texlua", "pdflatex", "pdftotext", "curl", "kpsewhich")
    )
)
CAN_LATEXMK_TEST = CAN_INSTALL_TEST and shutil.which("latexmk")
LATEXMK_TEST_ENGINES = [("-pdf", "pdflatex")]
LATEXMK_TEST_ENGINES.extend(
    (f"-{engine}", engine)
    for engine in ("xelatex", "lualatex")
    if shutil.which(engine)
)

SOURCE_PDF = r"\documentclass{article}\pagestyle{empty}\begin{document}%s\end{document}"
HOST_TEX = r"""\documentclass{article}\usepackage{pdfannex-docstore}
\begin{document}
\includedoc[page-style=empty]{memo}{Memo}
\includeannex[page-style=empty]{a.pdf}{Plain}
\end{document}
"""
SHOWCASE_TEX = r"""\documentclass[a4paper,11pt]{article}
\usepackage{pdfannex-docstore}
\pdfannexsetup{
    heading=Annexes,
    layout=footer-safe,
    page-style=plain
}
\begin{document}
Body.
\includeannex[label=one]{a1.pdf}{First}
\includeannex[label=three,layout=footer-safe]{a3.pdf}{Third}
\includeannex[layout=framed]{a1.pdf}{Framed}
\listofannexes
\section{Project summary}
The local appendix is \annexref{local} on page \annexpageref{local}.
The current project memo is \annexref{memo} on page \annexpageref{memo}.
\includeannex[label=local]{local.pdf}{Locally supplied appendix}
\includedoc[label=memo]{memo}{Project memo from the docstore}
\end{document}
"""


def run(command, cwd, env, check=True):
    return subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=check)


def make_pdf(cwd, name, text, env):
    (Path(cwd) / f"{name}.tex").write_text(SOURCE_PDF % text)
    run([shutil.which("pdflatex"), "-interaction=batchmode", f"{name}.tex"], cwd, env)


@unittest.skipUnless(CAN_PACKAGE, "l3build missing")
class AdapterPackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.project = Path(cls.tmp.name) / "project"
        cls.project.mkdir()
        for name in BUILD_INPUTS:
            source = HERE / name
            target = cls.project / name
            if source.is_dir():
                ignore = shutil.ignore_patterns("*.pdf") if name == "ctan" else None
                shutil.copytree(source, target, ignore=ignore)
            else:
                shutil.copy2(source, target)
        sidecar_scripts = cls.project.parent / "scripts"
        sidecar_scripts.mkdir()
        shutil.copy2(
            CORE / "scripts/install-texmfhome-tds.sh",
            sidecar_scripts / "install-texmfhome-tds.sh",
        )
        result = run(["make", "package"], cls.project, os.environ.copy(), check=False)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        cls.archive = cls.project / "pdfannex-docstore-ctan.zip"
        cls.tds_archive = cls.project / "build/distrib/tds/pdfannex-docstore.tds.zip"
        cls.core_tds_archive = None
        if CAN_INSTALL_TEST:
            core_project = Path(cls.tmp.name) / "core"
            core_project.mkdir()
            for name in CORE_BUILD_INPUTS:
                source = CORE / name
                target = core_project / name
                if source.is_dir():
                    shutil.copytree(source, target)
                else:
                    shutil.copy2(source, target)
            result = run(["l3build", "ctan"], core_project, os.environ.copy(), check=False)
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
            cls.core_tds_archive = core_project / "build/distrib/tds/pdfannex.tds.zip"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_ctan_and_tds_archives_contain_installable_files(self):
        with zipfile.ZipFile(self.archive) as ctan:
            ctan_names = set(ctan.namelist())
            mode = ctan.getinfo(
                "pdfannex-docstore/pdfannex-resolver-docstore"
            ).external_attr >> 16
            self.assertTrue(mode & 0o111, "CTAN resolver is not marked executable")
        for name in (
            "pdfannex-docstore/README.md",
            "pdfannex-docstore/LICENSE",
            "pdfannex-docstore/pdfannex-docstore.sty",
            "pdfannex-docstore/pdfannex-resolver-docstore",
            "pdfannex-docstore/adapter-lib.lua",
            "pdfannex-docstore/pdfannex-docstore-doc.tex",
            "pdfannex-docstore/pdfannex-docstore-doc.pdf",
            "pdfannex-docstore/pdfannex-resolver-docstore.1",
        ):
            self.assertIn(name, ctan_names)

        with zipfile.ZipFile(self.tds_archive) as tds:
            names = set(tds.namelist())
            for name in (
                "tex/latex/pdfannex-docstore/pdfannex-docstore.sty",
                "scripts/pdfannex-docstore/pdfannex-resolver-docstore",
                "scripts/pdfannex-docstore/adapter-lib.lua",
                "doc/latex/pdfannex-docstore/pdfannex-docstore-doc.pdf",
                "doc/man/man1/pdfannex-resolver-docstore.1",
            ):
                self.assertIn(name, names)
            mode = tds.getinfo(
                "scripts/pdfannex-docstore/pdfannex-resolver-docstore"
            ).external_attr >> 16
            self.assertTrue(mode & 0o111, "resolver script is not marked executable")

    @unittest.skipUnless(CAN_INSTALL_TEST, "TeX/curl tools missing")
    def test_installed_adapter_works_with_cli_and_locked_rebuild(self):
        for adapter_format in ("tds", "ctan"):
            with self.subTest(adapter_format=adapter_format):
                self.exercise_installed_adapter(adapter_format)

    def exercise_installed_adapter(self, adapter_format):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            texmf = work / "texmf"
            bindir = work / "bin"
            scripts = texmf / "scripts"
            cli_scripts = scripts / "pdfannex"
            adapter_scripts = scripts / "pdfannex-docstore"
            for directory in (bindir, cli_scripts):
                directory.mkdir(parents=True, exist_ok=True)
            adapter_scripts.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(self.tds_archive) as archive:
                archive.extractall(texmf)
            with zipfile.ZipFile(self.core_tds_archive) as archive:
                archive.extractall(texmf)

            if adapter_format == "ctan":
                with zipfile.ZipFile(self.archive) as archive:
                    archive.extractall(work / "ctan")
                package = work / "ctan/pdfannex-docstore"
                tex_dir = texmf / "tex/latex/pdfannex-docstore"
                tex_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(package / "pdfannex-docstore.sty", tex_dir)
                for name in ("pdfannex-resolver-docstore", "adapter-lib.lua"):
                    shutil.copy2(package / name, adapter_scripts)

            for script in (cli_scripts / "pdfannex", adapter_scripts / "pdfannex-resolver-docstore"):
                script.chmod(script.stat().st_mode | 0o111)
                (bindir / script.name).symlink_to(script)
            texlua = shutil.which("texlua")
            (bindir / "texlua").symlink_to(texlua)

            env = dict(
                os.environ,
                HOME=str(work),
                TEXMFHOME=str(texmf),
                TEXMFVAR=str(work / "texmf-var"),
                TEXMFCONFIG=str(work / "texmf-config"),
                PATH=f"{bindir}:{os.environ['PATH']}",
                PDFANNEX_DOCSTORE_TOKEN="test-token",
            )
            env.pop("TEXINPUTS", None)
            self.assertEqual(
                run(["kpsewhich", "pdfannex.sty"], work, env).stdout.strip(),
                str(texmf / "tex/latex/pdfannex/pdfannex.sty"),
            )
            self.assertEqual(
                run(["kpsewhich", "pdfannex-docstore.sty"], work, env).stdout.strip(),
                str(texmf / "tex/latex/pdfannex-docstore/pdfannex-docstore.sty"),
            )

            store = work / "store" / "memo"
            store.mkdir(parents=True)
            make_pdf(work, "rev1", "FIRST", env)
            (work / "rev1.pdf").rename(store / "1.pdf")
            make_pdf(work, "rev2", "LATEST", env)
            (work / "rev2.pdf").rename(store / "2.pdf")
            make_pdf(work, "a", "ALPHA", env)
            (work / "host.tex").write_text(HOST_TEX)

            server = DocstoreServer(work / "store", "test-token").start()
            env["PDFANNEX_DOCSTORE_URL"] = server.url
            try:
                run([str(bindir / "pdfannex"), "init"], work, env)
                run(["pdflatex", "-interaction=nonstopmode", "host.tex"], work, env, check=False)
                prepared = run([str(bindir / "pdfannex"), "prepare", "host.tex"], work, env)
                self.assertEqual(prepared.returncode, 0, prepared.stderr)
                lock = json.loads((work / "pdfannex.lock").read_text())
                self.assertEqual(
                    lock["sources"]["pdfannex://docstore/memo"]["resolved"],
                    "pdfannex://docstore/memo?rev=2",
                )
                self.assertIn("pdfannex://file/a.pdf", lock["sources"])

                if CAN_LATEXMK_TEST:
                    automated_projects = []
                    rc = run(
                        ["kpsewhich", "-format=texmfscripts", "pdfannex_latexmkrc"],
                        work,
                        env,
                    ).stdout.strip()
                    self.assertTrue(rc, "installed latexmk integration file not found")
                    latexmkrc = (
                        "my $pdfannex_rc = `kpsewhich -format=texmfscripts "
                        "pdfannex_latexmkrc`;\n"
                        "$pdfannex_rc =~ s/\\r?\\n\\z//;\n"
                        "die \"pdfannex latexmk integration not found\\n\" "
                        "unless $pdfannex_rc && -f $pdfannex_rc;\n"
                        "require $pdfannex_rc;\n"
                    )
                    for index, (flag, engine) in enumerate(LATEXMK_TEST_ENGINES):
                        automated = work / f"automated-{engine}"
                        automated.mkdir()
                        output_dir = automated
                        project_latexmkrc = latexmkrc
                        if index == 0:
                            output_dir = automated / "build"
                            output_dir.mkdir()
                            project_latexmkrc = "$out_dir = 'build';\n" + latexmkrc
                        automated_projects.append((flag, automated, output_dir))
                        for name, text in (
                            ("a1", "FIRSTANNEX"),
                            ("a3", "THIRDANNEX"),
                            ("local", "LOCALANNEX"),
                        ):
                            make_pdf(automated, name, text, env)
                        (automated / ".latexmkrc").write_text(project_latexmkrc)
                        (automated / "host.tex").write_text(SHOWCASE_TEX)
                        built = run(
                            [
                                "latexmk",
                                flag,
                                "-interaction=nonstopmode",
                                "-halt-on-error",
                                "host.tex",
                            ],
                            automated,
                            env,
                            check=False,
                        )
                        self.assertEqual(
                            built.returncode, 0, built.stdout + built.stderr
                        )
                        self.assertIn("Run number 2", built.stdout)
                        self.assertTrue((automated / "pdfannex.lock").is_file())
                        prepared = run(
                            [str(bindir / "pdfannex"), "verify", "host.tex"],
                            automated,
                            env,
                        )
                        self.assertIn("pdfannex: verify ok", prepared.stdout)
                        text = run(
                            ["pdftotext", str(output_dir / "host.pdf"), "-"],
                            automated,
                            env,
                        ).stdout
                        self.assertIn("LATEST", text)
                        for expected in (
                            "FIRSTANNEX",
                            "THIRDANNEX",
                            "LOCALANNEX",
                            "First",
                            "Third",
                            "Framed",
                            "Locally supplied appendix",
                            "Project memo from the docstore",
                        ):
                            self.assertIn(expected, text)
                        self.assertRegex(
                            text,
                            r"The local appendix is\s+Annex 4 on page \d+\.",
                        )
                        self.assertRegex(
                            text,
                            r"The current project memo is\s+Annex 5 on page \d+\.",
                        )

                    broken = work / "broken"
                    broken.mkdir()
                    (broken / ".latexmkrc").write_text(latexmkrc)
                    (broken / "missing.tex").write_text(
                        r"""\documentclass{article}
\usepackage{pdfannex-docstore}
\begin{document}
\includedoc{missing}{Missing}
\end{document}
"""
                    )
                    failed = run(
                        [
                            "latexmk",
                            "-pdf",
                            "-interaction=nonstopmode",
                            "-halt-on-error",
                            "missing.tex",
                        ],
                        broken,
                        env,
                        check=False,
                    )
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertIn("resource-not-found", failed.stdout + failed.stderr)
            finally:
                server.stop()

            shutil.rmtree(work / "store")
            (work / "a.pdf").unlink()
            if CAN_LATEXMK_TEST:
                for flag, automated, output_dir in automated_projects:
                    for name in ("a1.pdf", "a3.pdf", "local.pdf"):
                        (automated / name).unlink()
                    for suffix in (
                        ".aux",
                        ".fdb_latexmk",
                        ".fls",
                        ".log",
                        ".out",
                        ".pdf",
                    ):
                        (output_dir / f"host{suffix}").unlink(missing_ok=True)
                    offline = run(
                        [
                            "latexmk",
                            flag,
                            "-interaction=nonstopmode",
                            "-halt-on-error",
                            "host.tex",
                        ],
                        automated,
                        env,
                        check=False,
                    )
                    self.assertEqual(
                        offline.returncode, 0, offline.stdout + offline.stderr
                    )
                    text = run(
                        ["pdftotext", str(output_dir / "host.pdf"), "-"],
                        automated,
                        env,
                    ).stdout
                    self.assertIn("LATEST", text)
                    for expected in (
                        "FIRSTANNEX",
                        "THIRDANNEX",
                        "LOCALANNEX",
                        "First",
                        "Third",
                        "Framed",
                        "Locally supplied appendix",
                        "Project memo from the docstore",
                    ):
                        self.assertIn(expected, text)
                    self.assertRegex(
                        text,
                        r"The local appendix is\s+Annex 4 on page \d+\.",
                    )
                    self.assertRegex(
                        text,
                        r"The current project memo is\s+Annex 5 on page \d+\.",
                    )

            (work / "host.aux").unlink(missing_ok=True)
            (work / "host.pdf").unlink(missing_ok=True)
            run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "host.tex"], work, env)
            extracted = run(["pdftotext", "host.pdf", "-"], work, env).stdout
            self.assertIn("LATEST", extracted)
            self.assertIn("ALPHA", extracted)


if __name__ == "__main__":
    unittest.main()
