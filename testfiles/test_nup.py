"""Check that nup packs the pages of one annex onto shared sheets."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "testfiles"))
import locked  # noqa: E402
SRC = (
    r"\documentclass[a5paper]{article}\pagestyle{empty}"
    r"\begin{document}\Large P1\newpage P2\newpage P3\newpage P4\end{document}"
)
HOST = r"""\documentclass[a4paper]{article}\usepackage{pdfannex}
\begin{document}
Annex \annexref{a} on page \annexpageref{a}; annex \annexref{b} on page \annexpageref{b}.
\includeannex[nup=2x1,page-style=empty,label=a]{four.pdf}{Four}
\includeannex[page-style=empty,label=b]{four.pdf}{Plain}
\end{document}
"""


def pages(path, cwd):
    out = subprocess.run(["pdfinfo", path], cwd=cwd, capture_output=True, text=True,
                         check=True).stdout
    return int(next(l.split()[1] for l in out.splitlines() if l.startswith("Pages:")))


@unittest.skipUnless(shutil.which("pdflatex") and shutil.which("pdfinfo"), "tools missing")
class Nup(unittest.TestCase):
    def test_nup_shares_sheets_and_refs_point_to_first_sheet(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "four.tex").write_text(SRC)
            subprocess.run(["pdflatex", "-interaction=batchmode", "four.tex"], cwd=d,
                           check=True, capture_output=True)
            (d / "host.tex").write_text(HOST)
            env = {"PATH": os.environ["PATH"], "HOME": tmp, "TEXINPUTS": f"{ROOT / 'tex'}:"}
            locked.lock_inputs(d, "host", env, ["pdflatex", "-interaction=nonstopmode", "host.tex"])
            for _ in range(2):
                subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                                "host.tex"], cwd=d, check=True, capture_output=True, env=env)
            # 1 text page + 2 nup sheets + 4 plain pages
            self.assertEqual(pages("host.pdf", d), 7)
            text = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "host.pdf", "-"], cwd=d,
                                  capture_output=True, text=True, check=True).stdout
            self.assertIn("on page 2", text)
            self.assertIn("on page 4", text)


if __name__ == "__main__":
    unittest.main()
