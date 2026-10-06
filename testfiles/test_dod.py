"""The spec/15 Definition of Done example must build with latexmk on every engine."""

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
SOURCE = r"""\documentclass{article}\usepackage[%s,margin=0pt]{geometry}\pagestyle{empty}
\begin{document}\rule{3cm}{3cm}\newpage\rule{3cm}{3cm}\newpage\rule{3cm}{3cm}\newpage\rule{3cm}{3cm}\end{document}
"""
DOC = r"""\documentclass[a4paper]{article}
\usepackage{pdfannex}
\pdfannexsetup{ heading=Annexes, layout=footer-safe, page-style=plain }
\begin{document}
Main document.

See \annexref{contract}.

\listofannexes

\includeannex[ label=contract ]{letter-sized-contract.pdf}{ Contract }

\includeannex[ label=report, pages=1-3, frame=true ]{legal-sized-report.pdf}{ Report }
\end{document}
"""


def tool(cmd, cwd, env):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


@unittest.skipUnless(shutil.which("latexmk") and shutil.which("pdftotext"), "tools missing")
class DefinitionOfDone(unittest.TestCase):
    def test_example_builds_on_all_engines(self):
        for flag in ("-pdf", "-xelatex", "-lualatex"):
            with self.subTest(engine=flag), tempfile.TemporaryDirectory() as tmp:
                work = Path(tmp)
                env = {"PATH": os.environ["PATH"], "HOME": tmp, "TEXINPUTS": f"{ROOT / 'tex'}:"}
                for name, paper in (("letter-sized-contract", "letterpaper"),
                                    ("legal-sized-report", "legalpaper")):
                    (work / f"{name}.tex").write_text(SOURCE % paper)
                    tool(["pdflatex", "-interaction=batchmode", f"{name}.tex"], work, env)
                (work / "document.tex").write_text(DOC)
                locked.lock_inputs(work, "document", env, ["pdflatex", "-interaction=nonstopmode", "document.tex"])
                tool(["latexmk", flag, "-interaction=nonstopmode", "-halt-on-error", "document.tex"],
                     work, env)
                info = tool(["pdfinfo", "document.pdf"], work, env)
                self.assertIn("Pages:           8", info)  # 1 body + 4 contract + 3 report
                first = tool(["pdftotext", "-f", "1", "-l", "1", "document.pdf", "-"], work, env)
                self.assertIn("See Annex 1.", first)
                self.assertIn("Annex 1: Contract", first)
                self.assertIn("Annex 2: Report", first)


if __name__ == "__main__":
    unittest.main()
