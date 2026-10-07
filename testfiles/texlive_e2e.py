"""Exercise the pdfannex TDS package through TeX Live's package manager."""

import argparse
import io
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import zipfile

PDF_SOURCE = (
    r"\documentclass{article}\pagestyle{empty}\begin{document}%s\end{document}"
)
LATEXMKRC = r"""my $pdfannex_rc = `kpsewhich -format=texmfscripts pdfannex_latexmkrc`;
$pdfannex_rc =~ s/\r?\n\z//;
die "pdfannex latexmk integration not found\n"
    unless $pdfannex_rc && -f $pdfannex_rc;
require $pdfannex_rc;
"""


def run(command, cwd, env, check=True):
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    if check and result.returncode:
        raise RuntimeError(
            f"command failed ({result.returncode}): {command}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def tds_files(archive):
    files = {}
    with zipfile.ZipFile(archive) as package:
        for member in package.infolist():
            if member.is_dir():
                continue
            path = Path(member.filename)
            if path.is_absolute() or ".." in path.parts:
                raise RuntimeError(f"unsafe TDS archive path: {member.filename}")
            mode = (member.external_attr >> 16) & 0o777 or 0o644
            files[member.filename] = (package.read(member), mode)
    return files


def package_manifest(name, files, size=None):
    runfiles, docfiles = [], []
    run_size = doc_size = 0
    for path, (content, _) in sorted(files.items()):
        blocks = (len(content) + 511) // 512
        if path.startswith("doc/"):
            docfiles.append((path, blocks))
            doc_size += blocks
        else:
            runfiles.append((path, blocks))
            run_size += blocks

    lines = [
        f"name {name}",
        "category Package",
        "revision 1",
        "relocated 1",
    ]
    if size is not None:
        lines.append(f"containersize {size}")
    if runfiles:
        lines.append(f"runfiles size={run_size}")
        lines.extend(f" {path}" for path, _ in runfiles)
    if docfiles:
        lines.append(f"docfiles size={doc_size}")
        lines.extend(f" {path}" for path, _ in docfiles)
    return "\n".join(lines) + "\n"


def package_container(name, files, destination):
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"{name}.r1.tar.xz"
    size = 0
    for _ in range(8):
        manifest = package_manifest(name, files, size=size)
        contents = dict(files)
        contents[f"tlpkg/tlpobj/{name}.tlpobj"] = (manifest.encode(), 0o644)
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w:xz") as package:
            for path, (data, mode) in sorted(contents.items()):
                member = tarfile.TarInfo(path)
                member.size = len(data)
                member.mode = mode
                member.mtime = 0
                member.uid = member.gid = 0
                member.uname = member.gname = ""
                package.addfile(member, io.BytesIO(data))
        data = stream.getvalue()
        if len(data) == size:
            archive.write_bytes(data)
            return archive
        size = len(data)
    raise RuntimeError(f"container size did not converge for {name}")


def make_pdf(work, name, text, env):
    (work / f"{name}.tex").write_text(PDF_SOURCE % text, encoding="utf-8")
    run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"],
        work,
        env,
    )


def check_pdf_text(work, pdf_name, expected, env):
    text = run(["pdftotext", pdf_name, "-"], work, env).stdout
    for token in expected:
        if token not in text:
            raise RuntimeError(f"PDF output is missing {token!r}")


def enable_latexmk(work, env):
    (work / ".latexmkrc").write_text(LATEXMKRC, encoding="utf-8")
    result = run(
        ["kpsewhich", "-format=texmfscripts", "pdfannex_latexmkrc"],
        work,
        env,
    )
    if not result.stdout.strip():
        raise RuntimeError("pdfannex_latexmkrc is missing from the installed TDS tree")


def test_core(tds_archive):
    files = tds_files(tds_archive)
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        home = work / "home"
        usertree = home / "texmf"
        home.mkdir()
        env = dict(
            os.environ,
            HOME=str(home),
            TEXMFHOME=str(usertree),
            TEXMFVAR=str(home / "texmf-var"),
            TEXMFCONFIG=str(home / "texmf-config"),
        )
        env.pop("TEXINPUTS", None)
        tlmgr = shutil.which("tlmgr")
        if not tlmgr:
            raise RuntimeError("tlmgr is required for TeX Live package tests")
        if run(["kpsewhich", "pdfannex.sty"], work, env, check=False).stdout.strip():
            raise RuntimeError("pdfannex is visible before the package installation")

        archive = package_container("pdfannex", files, work / "containers")
        run(
            [tlmgr, "--usermode", "--usertree", str(usertree), "init-usertree"],
            work,
            env,
        )
        run(
            [
                tlmgr,
                "--usermode",
                "--usertree",
                str(usertree),
                "install",
                "--file",
                str(archive),
            ],
            work,
            env,
        )

        style = run(["kpsewhich", "pdfannex.sty"], work, env).stdout.strip()
        if style != str(usertree / "tex/latex/pdfannex/pdfannex.sty"):
            raise RuntimeError(f"pdfannex.sty resolved outside the test user tree: {style}")

        bindir = work / "bin"
        bindir.mkdir()
        cli = run(
            ["kpsewhich", "-format=texmfscripts", "pdfannex"], work, env
        ).stdout.strip()
        if not cli:
            raise RuntimeError("installed pdfannex CLI is missing from the TeX scripts tree")
        (bindir / "pdfannex").symlink_to(cli)
        env["PATH"] = f"{bindir}:{env['PATH']}"

        make_pdf(work, "annex", "COREFILEANNEX", env)
        (work / "document.tex").write_text(
            r"""\documentclass{article}
\usepackage{pdfannex}
\begin{document}
See \annexref{core}.
\listofannexes
\includeannex[label=core]{annex.pdf}{Core annex}
\end{document}
""",
            encoding="utf-8",
        )
        enable_latexmk(work, env)
        build = run(
            [
                "latexmk",
                "-pdf",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "document.tex",
            ],
            work,
            env,
        )
        if "Run number 2" not in build.stdout:
            raise RuntimeError("latexmk did not rerun the core build after request preparation")
        check_pdf_text(
            work,
            "document.pdf",
            ("COREFILEANNEX", "Annex 1: Core annex", "See Annex 1."),
            env,
        )
        run([str(bindir / "pdfannex"), "verify", "document.tex"], work, env)
        second_build = run(
            [
                "latexmk",
                "-pdf",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "document.tex",
            ],
            work,
            env,
        )
        if "Run number" in second_build.stdout:
            raise RuntimeError("the converged core latexmk build unexpectedly reran")
        check_pdf_text(work, "document.pdf", ("COREFILEANNEX",), env)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tds_archive", type=Path)
    args = parser.parse_args()
    test_core(args.tds_archive)
    print("OK: TeX Live core package installation passed")


if __name__ == "__main__":
    main()
