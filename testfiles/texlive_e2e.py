"""Exercise pdfannex TDS packages through TeX Live's package manager."""

import argparse
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapter-example"))
from docstore_server import DocstoreServer  # noqa: E402

PDF_SOURCE = r"\documentclass{article}\pagestyle{empty}\begin{document}%s\end{document}"
HOST_SOURCE = r"""\documentclass[a4paper,11pt]{article}
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


def package_manifest(
    name, files, dependency=None, root_prefix="", size=None, relocated=True
):
    runfiles, docfiles = [], []
    run_size = doc_size = 0
    for path, (content, _) in sorted(files.items()):
        package_path = f"{root_prefix}{path}"
        blocks = (len(content) + 511) // 512
        if path.startswith("doc/"):
            docfiles.append((package_path, blocks))
            doc_size += blocks
        else:
            runfiles.append((package_path, blocks))
            run_size += blocks

    lines = [
        f"name {name}",
        "category Package",
        "revision 1",
    ]
    if relocated:
        lines.append("relocated 1")
    if dependency:
        lines.append(f"depend {dependency}")
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


def write_local_repository(packages, destination, release_year):
    root = destination / "repository"
    texmf = root / "texmf-dist"
    (texmf / "web2c").mkdir(parents=True, exist_ok=True)
    (root / "tlpkg").mkdir(parents=True, exist_ok=True)
    database = [
        "name 00texlive.config",
        "category TLCore",
        "revision 1",
        f"depend release/{release_year}",
        "",
    ]
    for name, files, dependency in packages:
        manifest = package_manifest(
            name, files, dependency, root_prefix="texmf-dist/", relocated=False
        )
        database.extend((manifest.rstrip(), ""))
        for path, (content, mode) in files.items():
            target = texmf / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            target.chmod(mode)
    (root / "tlpkg/texlive.tlpdb").write_text("\n".join(database), encoding="utf-8")
    return root


def tl_release_year(tlmgr, cwd, env):
    version = run([tlmgr, "--version"], cwd, env).stdout
    match = re.search(r"TeX Live \S+ version (\d{4})", version)
    if not match:
        raise RuntimeError(f"cannot read TeX Live release year from: {version}")
    return match.group(1)


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
            raise RuntimeError("pdfannex is visible before the core package installation")
        archive = package_container("pdfannex", files, work / "containers")
        run([tlmgr, "--usermode", "--usertree", str(usertree), "init-usertree"], work, env)
        run([tlmgr, "--usermode", "--usertree", str(usertree),
             "install", "--file", str(archive)], work, env)

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


def test_adapter(core_archive, adapter_archive):
    packages = [
        ("pdfannex", tds_files(core_archive), None),
        ("pdfannex-docstore", tds_files(adapter_archive), "pdfannex"),
    ]
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        home = work / "home"
        home.mkdir()
        env = dict(os.environ, HOME=str(home), TEXMFHOME=str(home / "texmf"))
        env.pop("TEXINPUTS", None)
        tlmgr = shutil.which("tlmgr")
        if not tlmgr:
            raise RuntimeError("tlmgr is required for TeX Live package tests")
        for style in ("pdfannex.sty", "pdfannex-docstore.sty"):
            if run(["kpsewhich", style], work, env, check=False).stdout.strip():
                raise RuntimeError(f"{style} is visible before the adapter installation")
        release_year = tl_release_year(tlmgr, work, env)
        repository = write_local_repository(packages, work, release_year)

        result = run(
            [tlmgr, "--repository", str(repository), "install", "pdfannex-docstore"],
            work,
            env,
        )
        for package_name in ("pdfannex", "pdfannex-docstore"):
            info = run([tlmgr, "info", "--only-installed", package_name], work, env).stdout
            if not re.search(r"installed:\s+Yes\b", info):
                raise RuntimeError(
                    f"tlmgr did not install dependency {package_name}:\n{info}\n"
                    f"install output:\n{result.stdout}"
                )
        if "install: pdfannex " not in result.stdout:
            raise RuntimeError("installing the adapter did not pull in pdfannex as a dependency")
        for style in ("pdfannex.sty", "pdfannex-docstore.sty"):
            if not run(["kpsewhich", style], work, env).stdout.strip():
                raise RuntimeError(f"tlmgr installed the package without its {style}")

        bindir = work / "bin"
        bindir.mkdir()
        texmf_dist = run(["kpsewhich", "-var-value=TEXMFDIST"], work, env).stdout.strip()
        scripts = {"pdfannex": Path(texmf_dist) / "scripts/pdfannex/pdfannex"}
        scripts["pdfannex-resolver-docstore"] = (
            Path(texmf_dist)
            / "scripts/pdfannex-docstore/pdfannex-resolver-docstore"
        )
        for name, path in scripts.items():
            if not path.is_file():
                raise RuntimeError(f"installed TeX Live script is missing: {path}")
            (bindir / name).symlink_to(path)
        env["PATH"] = f"{bindir}:{env['PATH']}"
        env["PDFANNEX_DOCSTORE_TOKEN"] = "test-token"

        store = work / "store/memo"
        store.mkdir(parents=True)
        make_pdf(work, "rev1", "FIRSTREVISION", env)
        (work / "rev1.pdf").rename(store / "1.pdf")
        make_pdf(work, "rev2", "DOCSTOREANNEX", env)
        (work / "rev2.pdf").rename(store / "2.pdf")
        make_pdf(work, "a1", "FIRSTANNEX", env)
        make_pdf(work, "a3", "THIRDANNEX", env)
        make_pdf(work, "local", "LOCALANNEX", env)
        (work / "host.tex").write_text(HOST_SOURCE, encoding="utf-8")

        server = DocstoreServer(work / "store", "test-token").start()
        env["PDFANNEX_DOCSTORE_URL"] = server.url
        try:
            enable_latexmk(work, env)
            first_build = run(
                [
                    "latexmk",
                    "-lualatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "host.tex",
                ],
                work,
                env,
            )
            if "Run number 2" not in first_build.stdout:
                raise RuntimeError("latexmk did not rerun the adapter build after preparation")
            lock = json.loads((work / "pdfannex.lock").read_text(encoding="utf-8"))
            if lock["sources"]["pdfannex://docstore/memo"]["resolved"] != (
                "pdfannex://docstore/memo?rev=2"
            ):
                raise RuntimeError("docstore source did not lock the latest revision")
            for name in ("a1.pdf", "a3.pdf", "local.pdf"):
                if f"pdfannex://file/{name}" not in lock["sources"]:
                    raise RuntimeError(f"plain file source was not locked: {name}")
            run([str(bindir / "pdfannex"), "verify", "host.tex"], work, env)
            check_pdf_text(
                work,
                "host.pdf",
                (
                    "FIRSTANNEX",
                    "THIRDANNEX",
                    "LOCALANNEX",
                    "DOCSTOREANNEX",
                    "First",
                    "Third",
                    "Framed",
                    "Locally supplied appendix",
                    "Project memo from the docstore",
                ),
                env,
            )
            text = run(["pdftotext", "host.pdf", "-"], work, env).stdout
            if not re.search(r"The local appendix is\s+Annex 4 on page \d+\.", text):
                raise RuntimeError("local annex reference did not converge")
            if not re.search(r"The current project memo is\s+Annex 5 on page \d+\.", text):
                raise RuntimeError("docstore annex reference did not converge")
            second_build = run(
                [
                    "latexmk",
                    "-lualatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "host.tex",
                ],
                work,
                env,
            )
            if "Run number" in second_build.stdout:
                raise RuntimeError("the converged adapter latexmk build unexpectedly reran")
        finally:
            server.stop()

        shutil.rmtree(work / "store")
        for filename in ("a1.pdf", "a3.pdf", "local.pdf"):
            (work / filename).unlink()
        for suffix in (
            ".aux",
            ".fdb_latexmk",
            ".fls",
            ".log",
            ".out",
            ".pdf",
            ".toc",
        ):
            (work / f"host{suffix}").unlink(missing_ok=True)
        run(
            [
                "latexmk",
                "-lualatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "host.tex",
            ],
            work,
            env,
        )
        run([str(bindir / "pdfannex"), "verify", "host.tex"], work, env)
        check_pdf_text(
            work,
            "host.pdf",
            (
                "FIRSTANNEX",
                "THIRDANNEX",
                "LOCALANNEX",
                "DOCSTOREANNEX",
                "First",
                "Third",
                "Framed",
                "Locally supplied appendix",
                "Project memo from the docstore",
            ),
            env,
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("core", "adapter"))
    parser.add_argument("archives", nargs="+", type=Path)
    args = parser.parse_args()
    if args.mode == "core" and len(args.archives) == 1:
        test_core(args.archives[0])
    elif args.mode == "adapter" and len(args.archives) == 2:
        test_adapter(*args.archives)
    else:
        parser.error("core requires one TDS archive; adapter requires core and adapter TDS archives")
    print(f"OK: TeX Live {args.mode} package installation passed")


if __name__ == "__main__":
    main()
