class Parser:
    """ Parse the output of a "[COMMAND] --help" to different groupings and options. """
    def __init__(self, h):
        #print(repr(h))
        self.h = h.splitlines()
        #print(self.h)
        
        current_group = None # dummy
        self.args = {}
        self.usage = ""
        self.description = ""

        indent_0 = None # normal indentation (gets set, mostly 2)
        for l in self.h:
            #print(repr(l), "" == l.strip())
            if len(l.strip()) == 0:
                if current_group == "usage": current_group = "description"
                continue

            # identify sections
            if l.startswith("usage: "):
                self.usage += l[6:].strip()
                current_group = "usage"
                continue
            elif l.startswith("positional arguments:"):
                self.args["pos_raw"] = []
                self.args["pos"] = []
                current_group = "pos_raw"
                continue
            elif l.startswith("options:"):
                self.args["options_raw"] = []
                self.args["binary"] = []
                self.args["options"] = []
                current_group = "options_raw"
                continue

            #print(repr(l))
            # add options/arguments to section
            #if len(l.strip()) != 0:
            if current_group in ["options_raw", "pos_raw"]:
                indent = len(l) - len(l.lstrip())
                if indent_0 == None:
                    indent_0 = indent
                
                if indent > indent_0:
                    #print(l, self.args[current_group], current_group)
                    # this is a newline, but matching to the description
                    self.args[current_group][-1] += " " + l.lstrip()
                    continue


            match current_group:
                case "usage":
                    if l.strip() == "":
                        # ends the usage block
                        current_group = "description" # always follows after usage
                        #print(current_group, l)
                    else:
                        #print("aaaaaa", l, current_group, l.strip()=="")
                        self.usage += l.strip()
                case "pos_raw":
                    self.args["pos_raw"].append(l)
                    pass#print(repr(l))
                case "options_raw":
                    self.args["options_raw"].append(l)
                    pass#print(repr(l))
                case "description":
                    self.description += (" " + l.strip())

        self.description = self.description.strip()
        # actually split up the lines
        # for options and arguments
        for pos in self.args["pos_raw"]:
            self.args["pos"].append(self._positional_parse(pos))

        for opt in self.args["options_raw"]:
            is_bin, rdict = self._option_parse(opt)
            if is_bin:
                self.args["binary"].append(rdict)
            else:
                self.args["options"].append(rdict)
        

        #print("PARSE RESULTS")
        #print(self.description)
        #print("")
        #print(self.usage)
        #print("")
        #print(self.args["pos"])
        #print(self.args["binary"])
        #print(self.args["options"])

    def _positional_parse(self, s):
        """ Takes a string as parsed by the parser (pos_raw) and cleans it up to differentiate between name and description. Positional argument lines always consist of one single word name and a description
        """
        t = s.strip()
        first_whitespace = t.find(" ")
        rdict = {
            "name": t[:first_whitespace],
            "description": t[first_whitespace:].strip()
        }
        return rdict

    def _option_parse(self, s):
        """ Takes a string as parsed by the parser (options_raw) and cleans/splits it up. Determine if its an argument with a value or just a true/false argument.
        """
        t = s.strip()
        # find the longest whitespace in the string -> border between name(s) and description
        start_longest_whitespace = min(range(len(t)), key=lambda x: len(t[x:].strip()) - len(t[x:]))

        first = t[:start_longest_whitespace]#.strip()
        last = t[start_longest_whitespace:].strip()

        # find the longest name (assumed to be the best description)
        # firstly, removes the - and the second ha
        basename = first#first[1:].split(" ")[0]
        if first.find(",") != -1:
            basename = first.split(",")[1].strip()
        name = basename.split(" ")[0]

        #print(basename, name)
        # if the basename has no second half (like --clip CLIP), it is considered a binary argument
        is_bin = len(basename.split(" ")) == 1

        rdict = {
            "name": name,
            "description": last
        }
        return is_bin, rdict