module = "pdfannex-docstore"
sourcefiledir = "."
docfiledir = "ctan"
textfiledir = "ctan"
testfiledir = "testfiles/l3build"

sourcefiles = {
  "pdfannex-docstore.sty",
  "pdfannex-resolver-docstore",
  "adapter-lib.lua"
}
installfiles = { "pdfannex-docstore.sty" }
scriptfiles = { "pdfannex-resolver-docstore", "adapter-lib.lua" }
exefiles = { "pdfannex-resolver-docstore" }
typesetfiles = { "pdfannex-docstore-doc.tex" }
scriptmanfiles = { "pdfannex-resolver-docstore.1" }
textfiles = { "README.md", "LICENSE" }
