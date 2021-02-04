# ti842py

----

ti842py is a TI-BASIC to Python 3 transpiler. A transpiler is a piece of software that can convert code from one language to another. This program should be able to convert a lot of programs, but if you find something that it can't convert yet, start an issue.

# Features

----

 - Converts string literals to comments
 - `Disp`
 - Variable assignment
 - `If/Then/Else` statements, including `Else If`
 - `ClrHome`
 - `Input`
 - For loops
 - While loops
 - Repeat loops
 - `Pause`
 - `Wait`
 - `Stop`
 - `DelVar`
 - `Prompt`

### Planned Features
 - `Goto`
 - `Lbl`
 - `IS>(`
 - `DS<(`
 - `Return`
 - `getKey`
 - `eval()`/`expr()`
 - `toString()`
 - `Output()`

# Usage

----

ti742py can be used in 2 different ways. The first way is just running it from the command line. For example, if you wanted to convert the program in `tiprogram.txt` to `tiprogram.py`, you can this command: `ti842py -i tiprogram.txt -o tiprogram.py`. If no value is specified for `-o`, the converted program will be written to `stdout`.

ti842py can also be imported and used in a program. Here is an example program to convert `tiprogram.txt` to `tiprogram.py`:

```py
from ti842py import transpile

transpile("tiprogram.txt", "tiprogram.py")
```
Again, if the second argument is not supplied, the program will be written to `stdout`.