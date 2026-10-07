#!/usr/bin/env python3
"""Test release TDS artifacts with a clean native TeX Live user tree."""

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapter-example"))

from docstore_server import DocstoreServer  # noqa: E402
from test_package import SHOWCASE_TEX, make_pdf  # noqa: E402

LATEXMKRC = r"""$out_dir = 'build';
my $pdfannex_rc = `kpsewhich -format=texmfscripts pdfannex_latexmkrc`;
$pdfannex_rc =~ s/\r?\n\z//;
die "pdfannex latexmk integration not found\n"
    unless $pdfannex_rc && -f $pdfannex_rc;
require $pdfannex_rc;
"""
PDF_TOKENS = (
    "LATEST",
    "FIRSTANNEX",
    "THIRDANNEX",
    "LOCALANNEX",
    "First",
    "Third",
    "Framed",
    "Locally supplied appendix",
    "Project memo from the docstore",
)


def run(command, cwd, env, check=True):
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    if check and result.returncode:
        raise RuntimeError(
            f"command failed ({result.returncode}): {command}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def download_artifact(run_id, name, destination):
    run(
        [
            "gh",
            "run",
            "download",
            run_id,
            "--repo",
            "nocona71/pdfannex",
            "--name",
            name,
            "--dir",
            str(destination),
        ],
        ROOT,
        os.environ.copy(),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id", help="Actions run containing both TDS artifacts")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="pdfannex-release-tds-") as temporary:
        work = Path(temporary)
        core_artifacts = work / "artifacts/core"
        adapter_artifacts = work / "artifacts/docstore"
        core_artifacts.mkdir(parents=True)
        adapter_artifacts.mkdir(parents=True)
        download_artifact(args.run_id, "pdfannex-tds-archive", core_artifacts)
        download_artifact(
            args.run_id, "docstore-adapter-tds-archive", adapter_artifacts
        )

        core_archive = core_artifacts / "pdfannex.tds.zip"
        adapter_archive = adapter_artifacts / "pdfannex-docstore.tds.zip"
        core_installer = core_artifacts / "install-texmfhome-tds.sh"
        adapter_installer = adapter_artifacts / "install-texmfhome-tds.sh"
        for artifact in (
            core_archive,
            adapter_archive,
            core_installer,
            adapter_installer,
        ):
            if not artifact.is_file():
                raise RuntimeError(f"release artifact is missing: {artifact}")

        home = work / "home"
        texmfhome = work / "texmfhome"
        home.mkdir()
        texmfhome.mkdir()
        env = os.environ.copy()
        env.update(
            {
                "HOME": str(home),
                "TEXMFHOME": str(texmfhome),
                "TEXMFVAR": str(work / "texmf-var"),
                "TEXMFCONFIG": str(work / "texmf-config"),
                "PATH": (
                    f"{texmfhome / 'scripts/pdfannex'}:"
                    f"{texmfhome / 'scripts/pdfannex-docstore'}:"
                    f"{os.environ['PATH']}"
                ),
            }
        )
        env.pop("TEXINPUTS", None)

        before = run(
            ["kpsewhich", "pdfannex.sty"], work, env, check=False
        ).stdout.strip()
        if before:
            raise RuntimeError(
                f"pdfannex unexpectedly visible before TDS installation: {before}"
            )

        for installer, archive in (
            (core_installer, core_archive),
            (adapter_installer, adapter_archive),
        ):
            result = run(
                ["bash", str(installer), "install", str(archive), str(texmfhome)],
                work,
                env,
            )
            print(result.stdout.strip())

        for name, relative_path in (
            ("pdfannex.sty", "tex/latex/pdfannex/pdfannex.sty"),
            (
                "pdfannex-docstore.sty",
                "tex/latex/pdfannex-docstore/pdfannex-docstore.sty",
            ),
        ):
            resolved = Path(run(["kpsewhich", name], work, env).stdout.strip())
            expected = texmfhome / relative_path
            if resolved != expected:
                raise RuntimeError(f"{name} resolved to {resolved}; expected {expected}")

        project = work / "project"
        project.mkdir()
        for name, content in (
            ("a1", "FIRSTANNEX"),
            ("a3", "THIRDANNEX"),
            ("local", "LOCALANNEX"),
            ("memo", "LATEST"),
        ):
            make_pdf(project, name, content, env)

        store = work / "docstore"
        (store / "memo").mkdir(parents=True)
        shutil.copy2(project / "memo.pdf", store / "memo/1.pdf")
        (project / "showcase.tex").write_text(SHOWCASE_TEX, encoding="utf-8")
        (project / ".latexmkrc").write_text(LATEXMKRC, encoding="utf-8")

        for path in (
            project / "pdfannex.lock",
            project / ".pdfannex",
            project / "build",
        ):
            if path.exists():
                raise RuntimeError(f"test project is not clean: {path}")

        server = DocstoreServer(store, "test-token").start()
        try:
            env["PDFANNEX_DOCSTORE_URL"] = server.url
            env["PDFANNEX_DOCSTORE_TOKEN"] = "test-token"
            metadata = run(
                [
                    "curl",
                    "-fsS",
                    "-H",
                    "Authorization: Bearer test-token",
                    f"{server.url}/docs/memo",
                ],
                project,
                env,
            ).stdout.strip()
            print(f"Mock docstore: {metadata}")
            run(
                [
                    "curl",
                    "-fsS",
                    "-o",
                    os.devnull,
                    "-H",
                    "Authorization: Bearer test-token",
                    f"{server.url}/docs/memo/1.pdf",
                ],
                project,
                env,
            )

            build = run(
                [
                    "latexmk",
                    "-lualatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "showcase.tex",
                ],
                project,
                env,
                check=False,
            )
            output = build.stdout + build.stderr
            if build.returncode:
                raise RuntimeError(
                    f"initial latexmk failed ({build.returncode}):\n{output}"
                )
            if "Run number 2" not in output:
                raise RuntimeError(
                    "latexmk did not rerun after first-pass source preparation"
                )
            if not (project / "pdfannex.lock").is_file():
                raise RuntimeError("initial latexmk did not initialize pdfannex.lock")
            if not (project / ".pdfannex/resolved.tex").is_file():
                raise RuntimeError(
                    "initial latexmk did not create the resolution map"
                )

            verify = run(
                ["pdfannex", "verify", "showcase.tex"], project, env
            ).stdout
            if "verify ok" not in verify:
                raise RuntimeError(f"pdfannex verify failed:\n{verify}")
            text = run(
                ["pdftotext", "build/showcase.pdf", "-"], project, env
            ).stdout
            for token in PDF_TOKENS:
                if token not in text:
                    raise RuntimeError(f"PDF output is missing {token!r}")
            for reference in (
                r"The local appendix is\s+Annex 4 on page \d+\.",
                r"The current project memo is\s+Annex 5 on page \d+\.",
            ):
                if not re.search(reference, text):
                    raise RuntimeError(
                        f"PDF output is missing the expected reference: {reference}"
                    )
            print("pdfannex: verify ok")
            print(
                "PASS: clean TDS installation and initial latexmk build "
                "resolved the local and docstore annexes without manual init "
                "or prepare commands."
            )
        finally:
            server.stop()


if __name__ == "__main__":
    main()
