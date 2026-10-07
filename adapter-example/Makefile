.PHONY: test test-fast package clean
test:
	bash -n scripts/package
	python3 test_docstore.py
	python3 test_integration.py
	python3 test_package.py

test-fast:
	python3 test_package.py

package:
	./scripts/package

clean:
	l3build clean
	rm -f pdfannex-docstore-ctan.zip ctan/pdfannex-docstore-doc.pdf
