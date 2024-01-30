# Source:
# https://stackoverflow.com/a/63679316/33264
# see also https://github.com/junzis/pyModeS/blob/942c68dc7806183a99314f9665a90fa17f15ab42/build.py
# and
# https://github.com/RealistikDash/kcp.py/blob/193ff505cefb117217f767a47088354f6acaa58f/build.py
# and
# for doing a build with poetry
# https://github.com/python-poetry/poetry/issues/7470
# and
# https://github.com/EgorBlagov/trie-again/blob/0c478b0cd6eb02fb67f0127653105041c478f12f/build.py

import os

from Cython.Build import cythonize
from setuptools import Extension, Distribution
from shutil import copyfile as copy_file
from setuptools.command.build_ext import build_ext
from pathlib import Path

PACKAGE = "recython"


# This function will be executed in setup.py:
def build(setup_kwargs=None):
    if setup_kwargs is None:
        setup_kwargs = {}
    # The file you want to compile

    # gcc arguments hack: enable optimizations
    os.environ["CFLAGS"] = "-O3"

    extensions = [
        Extension(
            "recython.*",
            ["recython/**/*.py"],
            # extra_compile_args=[],
            define_macros=[("CYTHON_LIMITED_API", "1")],
            py_limited_api=True,
        )
    ]
    ext_modules = cythonize(extensions, compiler_directives={"language_level": "3"}, annotate=True)
    # One recipe
    # setup_kwargs.update(
    #     # {
    #     #     "ext_modules": cythonize(
    #     #         extensions,
    #     #         language_level=3,
    #     #         compiler_directives={"linetrace": True},
    #     #     ),
    #     #     "cmdclass": {"build_ext": build_ext},
    #     # }
    #     {
    #         "name": "recython",
    #         "ext_modules": cythonize(ext_modules, compiler_directives={"language_level": "3"}, annotate=True),
    #         "cmdclass": {"build_ext": build_ext},
    #     }
    # )

    # alternative recipe.
    distribution = Distribution(
        {
            "name": PACKAGE,
            "ext_modules": ext_modules,
        },
    )

    command = build_ext(distribution)
    command.ensure_finalized()  # type: ignore
    command.run()

    # Copy built extensions back to the project
    for output in map(Path, command.get_outputs()):  # type: ignore
        # relative_extension = os.path.relpath(output, command.build_lib)
        relative_extension = output.relative_to(command.build_lib)

        # throw if missing
        # if not output.exists():
        #     continue
        print(output, " --- ", relative_extension)
        copy_file(output, relative_extension)

        # unix magic
        mode = os.stat(relative_extension).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(relative_extension, mode)


if __name__ == "__main__":
    build()
