module = "pdfannex"

sourcefiledir = "tex"
docfiledir = "doc"
testfiledir = "testfiles"

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
