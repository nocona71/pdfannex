.PHONY: check test smoke doc package install clean

check:
	./scripts/check

test:
	l3build check

smoke:
	./scripts/smoke-tex

doc:
	./scripts/run-l3build doc

package:
	./scripts/run-l3build ctan

install:
	l3build install

clean:
	l3build clean
	rm -rf build
