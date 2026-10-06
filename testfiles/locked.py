"""Optional "locked" mode for the integration tests.

With PDFANNEX_TEST_LOCKED=1 a test first lets pdfannex.sty record its sources,
runs the CLI (bundled file resolver) to lock them, then deletes the original
PDFs. The test's normal build and assertions must then pass using only the
project-local artifact store, which proves the architecture end to end.
"""

import json
import os
from pathlib import Path
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "cli" / "pdfannex"
ENABLED = os.environ.get("PDFANNEX_TEST_LOCKED") == "1"


def lock_inputs(work, jobname, env, first_build):
    """No-op unless enabled. first_build is the command that writes the requests."""
    if not ENABLED:
        return
    work = Path(work)
    subprocess.run(first_build, cwd=work, check=True, capture_output=True, env=env)
    subprocess.run(["texlua", str(CLI), "prepare", f"{jobname}.tex"], cwd=work, check=True,
                   capture_output=True, env=env)
    lock = json.loads((work / "pdfannex.lock").read_text())
    assert lock["sources"], "nothing was locked"
    for uri in lock["sources"]:
        (work / unquote(uri.split("pdfannex://file/", 1)[1])).unlink()
    # Drop state from the first build so the real build starts from the lock only.
    for ext in ("aux", "pdf", "log", "out"):
        (work / f"{jobname}.{ext}").unlink(missing_ok=True)
