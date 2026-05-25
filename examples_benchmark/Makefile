.PHONY: all build build_fuzzy build_regression build_orbital bench clean

PYTHON := python

all: build bench

build: build_fuzzy build_regression build_orbital

build_fuzzy:
	cd fuzzy_arithmetic_cy && $(PYTHON) setup.py build_ext --inplace 2>&1

build_regression:
	cd multiple_regression_cy && $(PYTHON) setup.py build_ext --inplace 2>&1

build_orbital:
	cd orbital_mechanics_cy && $(PYTHON) setup.py build_ext --inplace 2>&1

bench:
	cd .. && $(PYTHON) -m examples_benchmark.benchmark

clean:
	rm -rf fuzzy_arithmetic_cy/build fuzzy_arithmetic_cy/*.c fuzzy_arithmetic_cy/*.html fuzzy_arithmetic_cy/*.so fuzzy_arithmetic_cy/*.pyd
	rm -rf multiple_regression_cy/build multiple_regression_cy/*.c multiple_regression_cy/*.html multiple_regression_cy/*.so multiple_regression_cy/*.pyd
	rm -rf orbital_mechanics_cy/build orbital_mechanics_cy/*.c orbital_mechanics_cy/*.html orbital_mechanics_cy/*.so orbital_mechanics_cy/*.pyd
