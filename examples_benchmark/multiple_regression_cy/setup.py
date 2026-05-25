from Cython.Build import cythonize
from setuptools import Extension, setup

setup(
    ext_modules=cythonize(
        Extension(
            "multiple_regression_cy",
            sources=["multiple_regression_cy.pyx"],
        ),
        compiler_directives={"language_level": "3"},
        annotate=True,
    )
)
