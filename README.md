# ti842py

[![PyPI version](https://badge.fury.io/py/ti842py.svg)](https://badge.fury.io/py/ti842py)
[![Downloads](https://pepy.tech/badge/ti842py)](https://pepy.tech/project/ti842py)
[![PyPI license](https://img.shields.io/pypi/l/ti842py.svg)](https://pypi.python.org/pypi/ti842py/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/TabulateJarl8/ti842py/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/TabulateJarl8/ti842py.svg)](https://GitHub.com/TabulateJarl8/ti842py/issues/)

----

ti842py is a TI-BASIC to Python 3 transpiler. A transpiler is a piece of software that can convert code from one language to another. This program should be able to convert a lot of programs, but if you find something that it can't convert yet, start an issue. This transpiler also has the ability to automatically decompile any 8Xp file that you supply as the input file, with the help of my other project that I contribute to, [basically-ti-basic](https://github.com/TabulateJarl8/basically-ti-basic). Note that this software is in beta and may produce inaccurate results.

# Features

----

 - Converts string literals to comments
 - `Disp`/`Output()`
 - Variable assignment
 - `If/Then/Else` statements, including `Else If`
 - `ClrHome`
 - `Input`/`Prompt`
 - For, While, and Repeat loops
 - `Pause`
 - `Wait`
 - `Stop`
 - `DelVar`
 - `getKey`
 - `Goto`/`Lbl`
 - `getDate` and `getTime`
 - `IS>(`/`DS<(`
 - `Menu()`
 - `toString()`
 - `randInt()`
 
### Planned Features
 - `Return`
 - `eval()`/`expr()`
 - `Ans`
 - List subscripting

### Known issues
 - Closing strings that have been left open breaks sometimes
 - Calling `Prompt` after `Output` will write to STDOUT over the Output

# Installation

----

ti842py can be installed via PyPI or by cloning the repository. To install it with PyPI, just run `pip3 install ti842py` in a terminal. To install it locally, you can clone the repository and run `python setup.py install --user`.

# Usage

----

ti842py can be used in 3 different ways. The first way is just running it from the command line. For example, if you wanted to convert the program in `tiprogram.txt` to `tiprogram.py`, you can this command: `ti842py -i tiprogram.txt -o tiprogram.py`. If no value is specified for `-o`, the converted program will be written to `stdout`. The `-n` flag can be added to force the transpiler to not decompile the input file, and the `-d` flag can be added to force the transpiler to attempt and decompile the input file. If the `--run` or `-r` argument is supplied, the resulting python file will be run after it is done transpiling

```
usage: ti842py [-h] [-o O] -i I [-n] [-d] [-r]

optional arguments:
  -h, --help            show this help message and exit
  -o O                  Optional output file to write to. Defaults to standard out.
  -i I                  Input file.
  -n, --force-normal    Forces the program to not attempt and decompile the input file. Useful for false positives
  -d, --force-decompile
                        Forces the program to attempt to decompile the input file
  -r, --run             Runs the program after it's done transpiling. Will not print to stdout
```

ti842py can also be imported and used in a program. Here is an example program to convert `tiprogram.txt` to `tiprogram.py`:

```py
from ti842py import transpile

transpile("tiprogram.txt", "tiprogram.py")
```
Again, if the second argument is not supplied, the program will be written to `stdout`. The `transpile` command can be supplied with 3 optional arguments, `decompileFile`, `forceDecompile`, and `run`. `decompileFile` defaults to `True`, and `forceDecompile` and `run` default to `False`

The last way that ti842py can be ran is by running the main python file. After cloning the repository, cd into the repository and run `python ti842py/main.py -i inputfile.txt`. You can supply any arguments that you would supply with the `ti842py` command.

# Special functions
----

 - `getKey` - The `getKey` function works just like it does in normal TI-BASIC, except with some special rules. Any key on the keyboard pressed will be converted to the corresponding key on the calculator. This works for letters, numbers, arrow keys, enter, delete, and symbols. As for the buttons not on a keyboard, the top 5 keys are the F1-F5 keys on the keyboard, `2nd` is alt, and `alpha` is ctrl. `mode` is F6, `stat` is f7, `vars` is F8, `clear` is F9, and the `X,T,θ,n` key is F10.

 - `If` - `If` blocks with `Then` after the `If` must be ended with `End`, they cannot be left open. `If` blocks on 2 lines without a `Then` cannot be closed with `End`
