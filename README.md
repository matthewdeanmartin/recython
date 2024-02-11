# recython
Use AI to assist in turning ordinary python into cython python.

Don't expect it to work unassisted. It is less ambitious than other coding assistants that try to do it all.

## Why cython?
- Compilation for speed.
- Compilation for obfuscation
- Compilation for calling from c/c++
Recython might help with the above.

- Wrap c/c++ code for calling from python
Recython has no features, yet, for creating wrappers.

## Approaches

### Compile as is with no changes 
This used to require renaming the file to .pyx and then compiling. I think the file renaming is optional.

See build.py, setup.py and pyproject.toml and build.yml for pointers.

This is the least likely to create interesting performance improvements.

One idea is to use cython [compilation as an obfuscator](https://www.youtube.com/watch?v=A1CqUVLda4g).


### Convert to .pxd and .pyx files
The bot gets a file by file prompt to create pyx and pxd headers using cython syntax. You can skip over problematic files.

### Convert to pure python cython
This differs from compiling as-is, in that here we import cython and use cython decorators and other patterns to 
recreate what the cython special syntax was doing in pyx files.

[Pure python cython](https://cython.readthedocs.io/en/stable/src/tutorial/pure.html) is a somewhat new approach and the bots are less familiar with it.

You import cython and use certain decorators and cython type annotations to get the performance improvements.

## Example

```python
from pathlib import Path
from dotenv import load_dotenv
import recython

load_dotenv()
project = Path("../examples/src_hangman/hangman")
recython.cythonize_classic_project(
    folder_path=project, target_folder=Path("./classic/"), never_translate=["__init__", "tests"]
)
```

## TODO
- Add config section to pyproject.toml
- Add a whole condensed manual to the prompts.
- switch between completion and chat models
- switch for particular model
- autoload .env file
- Attempt a compile and give the bot the error messages
- Code review bot.
- Log commentary as it is stripped off
- Maybe provide option to run a continuous conversation for additional context.
- Add a system prompt