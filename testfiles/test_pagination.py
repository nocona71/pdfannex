"""pagination=continue must record physical pages under scrlttr2 (resets page counter)."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "testfiles"))
import locked  # noqa: E402
DOC = r"""\documentclass{scrlttr2}
\usepackage{pdfannex}
\begin{document}
\begin{letter}{X}\opening{Hi}Body.\closing{Bye}\end{letter}
\begin{letter}{Y}\opening{Hi}Body.\closing{Bye}
\includeannex[label=a,pagination=%s]{a3.pdf}{Three}
\end{letter}
\end{document}
"""


def annex_page(mode):
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        shutil.copy(ROOT / "testfiles/support/a3.pdf", work)
        (work / "l.tex").write_text(DOC % mode)
        env = {"PATH": os.environ["PATH"], "HOME": tmp, "TEXINPUTS": f"{ROOT / 'tex'}:"}
        locked.lock_inputs(work, "l", env, ["pdflatex", "-interaction=nonstopmode", "l.tex"])
        for _ in range(2):
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "l.tex"],
                           cwd=work, check=True, capture_output=True, env=env)
        aux = (work / "l.aux").read_text()
        return int(re.search(r"\\pdfannex@newlabel\{a\}\{1\}\{(\d+)\}", aux).group(1))


@unittest.skipUnless(shutil.which("pdflatex"), "pdflatex missing")
class Pagination(unittest.TestCase):
    def test_inherit_follows_class_counter(self):
        self.assertEqual(annex_page("inherit"), 2)

    def test_continue_uses_physical_page(self):
        self.assertEqual(annex_page("continue"), 3)


if __name__ == "__main__":
    unittest.main()
