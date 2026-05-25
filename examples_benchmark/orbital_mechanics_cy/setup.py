from Cython.Build import cythonize
from setuptools import Extension, setup

setup(
    ext_modules=cythonize(
        Extension(
            "orbital_mechanics_cy",
            sources=["orbital_mechanics_cy.pyx"],
        ),
        compiler_directives={"language_level": "3"},
        annotate=True,
    )
)
