from Cython.Build import cythonize
from setuptools import Extension, setup

ext_modules = [
    Extension(
        "recython.*",
        ["recython/**/*.py"],
        # extra_compile_args=[],
        define_macros=[("CYTHON_LIMITED_API", "1")],
        py_limited_api=True,
    )
]
setup(
    name="recython",
    version="1.0.1",
    ext_modules=cythonize(ext_modules, compiler_directives={"language_level": "3"}, annotate=True),
)
