# guify

Build a GUI over any python script/program that supplies a standard self documentation (available with a --help, provided like by python's argparse).

Ironically, this is also a cli program.

Supports saving to/loading from a history of commands calls.

### Installation
1. Clone this repo
2. Go to the main directory of the repo (with `pyproject.toml` in it)
3. `pip install -e .`
    - If you also use anaconda, follow up with `conda develop .`
    - Depends on `pandas` & `tkinter`
4. Depending on your system, you need to make a small change in `guify/Guify.py` line 18
    - Change the list `["konsole", "--hold", "-e"]` to your individual terminal emulator, such that `konsole --hold -e 'echo Hello World!'` opens a new terminal window and prints `Hello World!`. The `--hold` is optional and depends on your use case.

### Usage
`python -m guify "python yourscript.py"` to start.

### Future improvements
- Chaining commands, useful for activating virtual environments.
- Piping commands, not that important for my usecases at the moment.