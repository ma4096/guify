#import os
import subprocess
import json
import pathlib

import pandas as pd
import tkinter as tk

from Parser import Parser

class Guify:
    """ Create a GUI on top of a normal cli command. Also allows for storing and loading commands.

    """

    version = "guify v0.2"
    keep_terminal = ["konsole", "--hold", "-e"] # launches new terminal, executes command appended to list and stays open after command terminates
    single_terminal = ["konsole", "-e"] # launches new terminal and executes command appended to list
    terminal = single_terminal

    wcol = 200 # width of each column

    def __init__(self, cmd):
        self.cmd = cmd

        self.dir = pathlib.Path(__file__).parent
        # stty cols 1000 sets the width of the terminal window, making it easier to parse
        #print(subprocess.check_output("tput cols", shell=True, text=True))
        self.parsetext = subprocess.check_output(cmd + " --help", shell=True, text=True)
        #print(self.parsetext)
        
        self.parser = Parser(self.parsetext)
        self.mandatory_order = [dic["name"] for dic in self.parser.args["pos"]]

        # prepare arguments
        #self.binary_arguments = []
        #self.optional_arguments = {}
        #self.mandatory_arguments = {}

        self.build_gui(self.parser)
        self.load_history()

        self.root.mainloop() # gets defined in build_gui

    def build_gui(self, parser=None):
        """ Take the parser results and build the tkinter gui """
        self.var_objects = {}

        if parser == None:
            parser = self.parser

        self.root = tk.Tk()#screenName = self.version)
        self.root.title(self.version)
        #self.root.iconbitmap((self.dir / "favicon.ico").resolve())
        #self.root.iconbitmap("favicon.ico")
        #root.geometry("600x400")

        # add usage and description
        usage = tk.Label(self.root, text = parser.usage, wraplength=2*self.wcol, justify="left")
        usage.grid(row=0, column=0, columnspan=2, sticky="W")
        description = tk.Label(self.root, text = parser.description, wraplength=3*self.wcol, justify="left")
        description.grid(row=1, column=0, columnspan=3, sticky="W")

        grid_row = 2

        # add mandatory and optional arguments
        for k in parser.args["pos"] + parser.args["options"]:
            #val = parser.args["pos"][k]
            var = tk.StringVar()
            self.var_objects[k["name"]] = var
            pos_name = tk.Label(self.root, text = k["name"], wraplength=self.wcol, justify="left")
            pos_description = tk.Label(self.root, text = k["description"], wraplength=self.wcol, justify="left")
            pos_entry = tk.Entry(self.root, textvariable=var)
            
            pos_name.grid(row=grid_row, column=1, sticky="W")
            pos_description.grid(row=grid_row, column=2, sticky="W")
            pos_entry.grid(row=grid_row, column=0, sticky="E")
            grid_row += 1


        # add binary arguments
        for k in parser.args["binary"]:
            var = tk.StringVar(value="False")
            self.var_objects[k["name"]] = var
            tick = tk.Checkbutton(self.root, variable=var, onvalue="True", offvalue="False")
            pos_name = tk.Label(self.root, text = k["name"], wraplength=self.wcol, justify="left")
            pos_description = tk.Label(self.root, text = k["description"], wraplength=self.wcol, justify="left")

            tick.grid(row=grid_row, column=0, sticky="E")
            pos_name.grid(row=grid_row, column=1, sticky="W")
            pos_description.grid(row=grid_row, column=2, sticky="W")
            grid_row += 1

        # add interaction buttons
        # button for executing the command
        execute = tk.Button(self.root, text="execute",command=self.execute)
        execute.grid(row=grid_row, column=0)

        # button for selecting to keep or exit the console afterwards
        boolVar = tk.BooleanVar(value=False)
        def switch_terminal():
            self.terminal = self.keep_terminal if boolVar.get() else self.single_terminal

        tick = tk.Checkbutton(self.root, text="Keep console open", var=boolVar, onvalue=True, offvalue=False, command=switch_terminal)
        tick.grid(row=grid_row+1, column=0)

        # button and textfield for only showing the command
        show = tk.Button(self.root, text="show command", command=self.show_command)
        self.show_out = tk.Text(self.root, width=50, height=2 )#, textvariable=self.show_var)
        show.grid(row=grid_row, column=1)
        self.show_out.grid(row=grid_row+1, column=1, columnspan=2)

        # button for saving the current command to the history
        save = tk.Button(self.root, text="save to history", command=self.add_command_to_history)
        save.grid(row=grid_row, column=2)

        #print(self.var_objects)
        #for k in self.var_objects:
        #    obj = self.var_objects[k]
        #    print(k, obj.get())

    def execute(self):
        """ Compile and execute the command """
        parsed = self.compile()
        cmd = self.build_command(parsed)
        #print(self.terminal + [cmd])
        subprocess.call(self.terminal + [cmd])

    def show_command(self):
        """ Compile and show the command, dont execute it """
        parsed = self.compile()
        cmd = self.build_command(parsed)
        #self.show_var.set(cmd)
        self.write_to_gui(cmd)
        #self.show_out.insert("end", cmd)

    def compile(self):
        """ Collects the values from the previously build GUI vars and builds the command """
        parsed_values = {}
        #print(self.var_objects)
        for k in self.var_objects:
            val = self.var_objects[k].get()
            parsed_values[k] = val# if type(val) != int else 
            #print(k, type(val))

        #print("PARSED VALS:", parsed_values)
        return parsed_values

    def decompile(self, var):
        """ Starting from a dictionary of values, set the variables in the tk window accordingly """
        #print(var)
        for k in var:
            val = var[k]
            self.var_objects[k].set(val)

    #def build_command(self, binary_arguments, optional_arguments, mandatory_arguments):
    def build_command(self, var_objects):
        """ Compile all configs to the final command. Throw warnings for special shell escape characters 
        
        :param list binary_arguments: list with the binary arguments (no value, only) 
        """
        # base command
        cmd = self.cmd + " "

        # binary, optional arguments: only add when the value exists in var_objects
        cmd += " ".join([opt["name"] for opt in self.parser.args["binary"] if var_objects[opt["name"]] == "True"]) + " "

        # optional arguments
        for k in self.parser.args["options"]:
            name = k["name"]
            val = var_objects[name]
            if val != "":
                cmd += str(name) + " " + str(val) + " "
        
        # mandatory arguments -> ensure the order of arguments
        cmd += " ".join([str(var_objects[k]) for k in self.mandatory_order])
        #print(cmd)
        return cmd

    def write_to_gui(self, s):
        """ Writes to the show_out text field, replaces old text """
        self.show_out.delete("1.0", tk.END)
        self.show_out.insert("end", s)

    #%% Methods for handling history
    def load_history(self):
        """ Load the history of the command. Must be executed after building the GUI """
        self.history = []

        path = (self.dir / "history" / (self.cmd.replace(" ", "_") + ".csv"))
        self.history_file = path.resolve()
        
        self.df = 0
        if path.exists(): 
            print("History exists, loading history for " + self.cmd)
            self.df = pd.read_csv(self.history_file, sep="\t", dtype=str, keep_default_na=False)
            self.build_history_menu()
        else:
            print("History for '" + self.cmd + "' does not exist yet. Will get created when saving a command.")
            #self.df = pd.DataFrame({k: [v] for k,v in self.compile().items()})
            self.df = pd.DataFrame(columns=self.compile().keys())

        #print(self.df)

    def build_history_menu(self):
        """ Build the menu button for selecting commands from history """
        menubutton = tk.Menubutton(self.root, text="history")
        menubutton.menu = tk.Menu(menubutton) 
        menubutton["menu"]= menubutton.menu

        def create_decompile_lambda(conf=None):
            return lambda: self.decompile(conf)

        for index, row in self.df.iterrows():
            config = row.to_dict()
            #print(config)
            menubutton.menu.add_radiobutton(label=self.build_command(config), command=create_decompile_lambda(config))#self.decompile(config.copy()))

        menubutton.grid(row=0, column=2)

    def add_command_to_history(self):
        parsed = self.compile()

        #self.df.insert(len(self.df), parsed)
        new_df = pd.DataFrame.from_dict({k: [parsed[k]] for k in parsed})

        # check if this config already exists without using external
        exists = False
        if len(self.df) > 0:
            merged = pd.merge(self.df, new_df, how="left", indicator="exists")
            exists = len([True for x in (merged.exists == "both").to_list() if x]) > 0

        if not exists:
            self.df = pd.concat((self.df, new_df))
            #print(self.df)
            self.df.to_csv(self.history_file, sep="\t", index=False)
            self.write_to_gui("Wrote configuration for '" + self.build_command(parsed) + "' to history.")
            
            self.build_history_menu()
        else:
            # the row already exists
            self.write_to_gui("This command already exists in the history, did not get saved a second time.")

        #print("DF after adding:")
        #print(self.df)