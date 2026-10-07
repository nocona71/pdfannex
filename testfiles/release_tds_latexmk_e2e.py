#!/usr/bin/env python3
"""Test the released core TDS archive with a clean native TeX Live user tree."""

import argparse
import os
from pathlib import Path
import subprocess
import tempfile


def run(command, cwd, env, check=True):
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    if check and result.returncode:
        raise RuntimeError(
            f"command failed ({result.returncode}): {command}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def download_artifact(run_id, destination):
    run(
        [
            "gh",
            "run",
            "download",
            run_id,
            "--repo",
            "nocona71/pdfannex",
            "--name",
            "pdfannex-tds-archive",
            "--dir",
            str(destination),
        ],
        Path.cwd(),
        os.environ.copy(),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id", help="Actions run containing the core TDS artifact")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="pdfannex-release-tds-") as temporary:
        work = Path(temporary)
        artifacts = work / "artifacts"
        artifacts.mkdir()
        download_artifact(args.run_id, artifacts)

        archive = artifacts / "pdfannex.tds.zip"
        installer = artifacts / "install-texmfhome-tds.sh"
        for artifact in (archive, installer):
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
                "PATH": f"{texmfhome / 'scripts/pdfannex'}:{os.environ.get('PATH', '')}",
            }
        )
        env.pop("TEXINPUTS", None)

        before = run(["kpsewhich", "pdfannex.sty"], work, env, check=False).stdout.strip()
        if before:
            raise RuntimeError(f"pdfannex unexpectedly visible before installation: {before}")

        result = run(
            ["bash", str(installer), "install", str(archive), str(texmfhome)],
            work,
            env,
        )
        print(result.stdout.strip())
        resolved = run(["kpsewhich", "pdfannex.sty"], work, env).stdout.strip()
        expected = texmfhome / "tex/latex/pdfannex/pdfannex.sty"
        if Path(resolved) != expected:
            raise RuntimeError(f"pdfannex.sty resolved to {resolved}; expected {expected}")

        project = work / "project"
        project.mkdir()
        (project / "annex.tex").write_text(
            r"\documentclass{article}\pagestyle{empty}\begin{document}"
            r"LOCKEDANNEX\end{document}",
            encoding="utf-8",
        )
        run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "annex.tex",
            ],
            project,
            env,
        )
        (project / "annex.pdf").rename(project / "local.pdf")
        (project / ".latexmkrc").write_text(
            r"""$out_dir = 'build';
my $pdfannex_rc = `kpsewhich -format=texmfscripts pdfannex_latexmkrc`;
$pdfannex_rc =~ s/\r?\n\z//;
die "pdfannex latexmk integration not found\n"
    unless $pdfannex_rc && -f $pdfannex_rc;
require $pdfannex_rc;
""",
            encoding="utf-8",
        )
        (project / "showcase.tex").write_text(
            r"""\documentclass{article}
\usepackage{pdfannex}
\begin{document}
See \annexref{local} on page \annexpageref{local}.
\listofannexes
\includeannex[label=local]{local.pdf}{Local appendix}
\end{document}
""",
            encoding="utf-8",
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
        )
        if "Run number 2" not in build.stdout:
            raise RuntimeError("latexmk did not rerun after source preparation")
        if not (project / "pdfannex.lock").is_file():
            raise RuntimeError("initial latexmk did not initialize pdfannex.lock")
        if not (project / ".pdfannex/resolved.tex").is_file():
            raise RuntimeError("initial latexmk did not create the resolution map")

        verify = run(
            ["pdfannex", "verify", "showcase.tex"], project, env
        ).stdout
        if "verify ok" not in verify:
            raise RuntimeError(f"pdfannex verify failed:\n{verify}")
        text = run(["pdftotext", "build/showcase.pdf", "-"], project, env).stdout
        for token in ("LOCKEDANNEX", "Annex 1: Local appendix", "See Annex 1 on page"):
            if token not in text:
                raise RuntimeError(f"PDF output is missing {token!r}")

        second_build = run(
            [
                "latexmk",
                "-lualatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "showcase.tex",
            ],
            project,
            env,
        )
        if "Run number" in second_build.stdout:
            raise RuntimeError("the converged build unexpectedly reran")

        (project / "local.pdf").unlink()
        run(
            [
                "latexmk",
                "-g",
                "-lualatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "showcase.tex",
            ],
            project,
            env,
        )
        run(["pdfannex", "verify", "showcase.tex"], project, env)
        text = run(["pdftotext", "build/showcase.pdf", "-"], project, env).stdout
        if "LOCKEDANNEX" not in text:
            raise RuntimeError("locked rebuild did not use the stored annex")
        print(
            "PASS: clean core TDS installation and first latexmk build; "
            "locked rebuild succeeded after removing the source PDF."
        )


if __name__ == "__main__":
    main()
