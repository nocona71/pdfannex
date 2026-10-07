module = "pdfannex"
ctanpkg = "pdfannex"

uploadconfig = {
  author = "Toni Incog",
  bugtracker = "https://github.com/nocona71/pdfannex/issues",
  ctanPath = "macros/latex/contrib/pdfannex",
  description = "Include external PDF files as semantic annexes in LaTeX documents.",
  email = os.getenv("CTAN_EMAIL"),
  home = "https://github.com/nocona71/pdfannex",
  license = { "lppl1.3c" },
  pkg = "pdfannex",
  repository = "https://github.com/nocona71/pdfannex",
  summary = "Include external PDFs as semantic annexes in LaTeX documents",
  uploader = "Toni Incog",
}

if os.getenv("PDFANNEX_CTAN_UPLOAD") == "true" then
  ctanupload = true
end

sourcefiledir = "tex"
docfiledir = "doc"
testfiledir = "testfiles"
docfiles = { "examples/" }

sourcefiles = { "pdfannex.sty" }
installfiles = { "pdfannex.sty" }
typesetfiles = { "pdfannex-doc.tex" }

checkengines = { "pdftex", "luatex", "xetex" }
checkruns = 2
supportdir = "testfiles/support"

textfiles = {
  "README.md",
  "CHANGELOG.md",
  "LICENSE"
}

tdsdirs = {
  ["cli"] = "scripts/pdfannex"
}
exefiles = { "pdfannex" }
scriptmanfiles = { "pdfannex.1" }
