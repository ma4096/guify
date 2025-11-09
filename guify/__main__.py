from .Guify import Guify

import argparse

def main():

    parser = argparse.ArgumentParser(description="Generates an input mask for any python command line tool that generates a help page using the argparse library (--help). Calls can be stored in its library, allowing to edit and re-run commands.")
    parser.add_argument("command", type=str, help="Command to execute")
    parser.add_argument("-r", "--read", action="store_true", help="Look for a configuration file in guify/commands to generate the GUI. Useful for tools that generate a help page with another standard formatting.")

    args = parser.parse_args()
    cmd = "python -m utils_external.cv.frameGetter"
    g = Guify(args.command, from_file=args.read)

if __name__=="__main__":
    #g.build_gui()
    main()
