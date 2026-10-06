"""Check that annexes keep the host sheet size and honour margin/footer-space."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "testfiles"))
import locked  # noqa: E402
RULE = (
    r"\documentclass{article}\usepackage[%s,margin=0pt]{geometry}"
    r"\pagestyle{empty}\setlength\parindent{0pt}"
    r"\begin{document}\noindent\rule{\paperwidth}{\paperheight}\end{document}"
)
HOST = r"""\documentclass[a4paper]{article}\usepackage{pdfannex}
\begin{document}
\includeannex[page-style=empty]{small.pdf}{small}
\includeannex[page-style=empty]{big.pdf}{big}
\includeannex[page-style=empty]{wide.pdf}{wide}
\includeannex[page-style=empty,margin=20mm,footer-space=30mm]{full.pdf}{custom}
\end{document}
"""


def run(cmd, cwd, env=None):
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, env=env)


def extent(path):
    """Return (top, bottom, left, right) gaps in pixels around dark content."""
    data = path.read_bytes().split(b"\n", 3)
    width, height = map(int, data[1].split())
    px = data[3]
    dark = lambda x, y: px[y * width + x] < 60
    rows = [y for y in range(height) if any(dark(x, y) for x in range(0, width, 2))]
    cols = [x for x in range(width) if any(dark(x, y) for y in range(0, height, 2))]
    return rows[0], height - 1 - rows[-1], cols[0], width - 1 - cols[-1]


@unittest.skipUnless(shutil.which("pdflatex") and shutil.which("pdftoppm"), "tools missing")
class Geometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        for name, paper in [("small", "a5paper"), ("big", "a3paper"),
                            ("wide", "a4paper,landscape"), ("full", "a4paper")]:
            (cls.dir / f"{name}.tex").write_text(RULE % paper)
            run(["pdflatex", "-interaction=batchmode", f"{name}.tex"], cls.dir)
        (cls.dir / "host.tex").write_text(HOST)
        env = {"PATH": __import__("os").environ["PATH"], "HOME": str(cls.dir),
               "TEXINPUTS": f"{ROOT / 'tex'}:"}
        locked.lock_inputs(cls.dir, "host", env, ["pdflatex", "-interaction=nonstopmode", "host.tex"])
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "host.tex"], cls.dir, env)
        run(["pdftoppm", "-r", "72", "-gray", "host.pdf", "p"], cls.dir)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_sheet_size_is_preserved(self):
        info = subprocess.run(["pdfinfo", "-f", "1", "-l", "4", "host.pdf"], cwd=self.dir,
                              capture_output=True, text=True, check=True).stdout
        sizes = [l for l in info.splitlines() if "size:" in l and l.startswith("Page")]
        self.assertEqual(len(sizes), 4)
        for line in sizes:
            self.assertIn("A4", line)

    def test_small_page_is_enlarged_to_fit(self):
        # Documented limitation (decision 0008): A5 is scaled up to the A4 sheet.
        top, bottom, left, right = extent(self.dir / "p-1.pgm")
        self.assertLessEqual(max(top, bottom, left, right), 3)

    def test_oversized_page_is_shrunk_and_wide_page_not_rotated(self):
        top, bottom, left, right = extent(self.dir / "p-2.pgm")
        self.assertLessEqual(max(top, bottom, left, right), 3)
        top, bottom, left, right = extent(self.dir / "p-3.pgm")
        self.assertLessEqual(max(left, right), 3)  # width-limited, centered vertically
        self.assertGreater(min(top, bottom), 150)

    def test_margin_and_footer_space(self):
        top, bottom, left, right = extent(self.dir / "p-4.pgm")
        mm = 72 / 25.4
        self.assertAlmostEqual(top, 20 * mm, delta=3)
        self.assertAlmostEqual(bottom, 50 * mm, delta=3)
        # Width is limited by the height here, so side gaps are at least the margin.
        self.assertGreaterEqual(left, 20 * mm - 3)
        self.assertGreaterEqual(right, 20 * mm - 3)


if __name__ == "__main__":
    unittest.main()
