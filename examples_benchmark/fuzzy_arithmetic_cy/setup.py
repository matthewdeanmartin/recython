from Cython.Build import cythonize
from setuptools import Extension, setup

setup(
    ext_modules=cythonize(
        Extension(
            "fuzzy_arithmetic_cy",
            sources=["fuzzy_arithmetic_cy.pyx"],
        ),
        compiler_directives={"language_level": "3"},
        annotate=True,
    )
)
