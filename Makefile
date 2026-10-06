.PHONY: check test smoke e2e doc package adapter-package install clean

check:
	./scripts/check

test:
	l3build check

smoke:
	./scripts/smoke-tex

e2e: package
	./scripts/e2e-ctan build/pdfannex-ctan.zip

doc:
	./scripts/run-l3build doc

package:
	./scripts/run-l3build ctan

adapter-package:
	$(MAKE) -C adapter-example package

install:
	l3build install

clean:
	l3build clean
	$(MAKE) -C adapter-example clean
	rm -rf build
