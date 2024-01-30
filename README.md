# recython
Use ai to assist in turning ordinary python into cython python.

Don't expect it to work unassisted.

Less ambitious than other coding assistants that try to do it all.

## Two approaches
- Convert to .pxd and .pyx files
- Convert to [pure python cython](https://cython.readthedocs.io/en/stable/src/tutorial/pure.html)

## Implemented
- looping across files
- loads templates
- skips files that should not be translated
- Reminds bot of some cython pointers
- Tell bot to put advice in headers.
- Strips off code block boundaries and commentary.

## TODO
- Add a whole condensed manual to the prompts.
- switch between completion and chat models
- switch for particular model
- autoload .env file
- Attempt a compile and give the bot the error messages
- Code review bot.
- Log commentary as it is stripped off
- Maybe provide option to run a continuous conversation for additional context.
- Add a system prompt