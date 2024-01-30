# from Cython.Build import cythonize
# from Cython.Compiler.Errors import CompileError
#
# def check_cython_code(filename):
#     try:
#         # Parse the Cython code. This will raise a CompileError if there's a syntax error
#         cythonize(filename, language_level=3)
#         print(f"{filename} parsed successfully.")
#     except CompileError as e:
#         print(f"Compilation error in {filename}:")
#         print(e)
