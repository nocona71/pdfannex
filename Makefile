.PHONY: check test test-fast smoke e2e doc package install clean

check:
	./scripts/check

test:
	l3build check

test-fast:
	python3 testfiles/test_packaging.py
	python3 testfiles/test_tds_installer.py

smoke:
	./scripts/smoke-tex

e2e: package
	./scripts/e2e-ctan build/pdfannex-ctan.zip

doc:
	./scripts/run-l3build doc

package:
	./scripts/run-l3build ctan

install:
	l3build install

clean:
	l3build clean
	rm -rf build
