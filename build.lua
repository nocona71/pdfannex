module = "pdfannex"

sourcefiledir = "tex"
docfiledir = "doc"
testfiledir = "testfiles"

sourcefiles = { "pdfannex.sty" }
installfiles = { "pdfannex.sty" }
typesetfiles = { "pdfannex-doc.tex" }

checkengines = { "pdftex", "luatex", "xetex" }
checkruns = 1

textfiles = {
  "README.md",
  "CHANGELOG.md",
  "LICENSE"
}
