from Guify import Guify

import argparse

def main():

    parser = argparse.ArgumentParser(description="Generates an input mask for any python command line tool that generates a help page using the argparse library (--help). Stores every call to its library, allowing to edit and re-run commands.")
    parser.add_argument("command", type=str, help="Command to execute")

    args = parser.parse_args()
    cmd = "python -m utils_external.cv.frameGetter"
    g = Guify(args.command)

if __name__=="__main__":
    #g.build_gui()
    main()