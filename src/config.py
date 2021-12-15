# to do: I want to make recursiveParse default to true

import argparse

class args:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument("directory", type=str, help="directory name") 
        parser.add_argument("filename", nargs='?', type=str, help="file to parse", default='main')
        parser.add_argument("-t", "--test", action="store_true")
        
        parser.add_argument("-s", "--removeSysfuncs", dest='removeSysfuncs', action="store_true", help="removes irrelevant (not related to syscalls) funccalls")
        parser.add_argument("--no-removeSysfuncs", dest = 'removeSysfuncs', action="store_false", help="turn off remove irrelevant (no related to syscalls) funccalls")
        parser.set_defaults(removeSysfuncs = True)

        parser.add_argument("-e", "--takeallev", dest="takeallev", action="store_true")
        parser.add_argument("--no-takeallev", dest="takeallev", action="store_false")
        parser.set_defaults(takeallev = True)

        parser.add_argument("-d", "--debug", action="store_true")
        parser.add_argument("-p", "--printArgs", action="store_true")

        parser.add_argument("-r", "--recursiveParse", dest='recursiveParse', action="store_true", help="either to recursively parse all the functions")
        parser.add_argument("--no-recursiveParse", dest='recursiveParse', action="store_false", help="turn off recursive parse")
        parser.set_defaults(recursiveParse = True)

        _args = parser.parse_args()

        self.directory = _args.directory
        self.filename = _args.filename

        self.test = _args.test
        self.removeSysfuncs = _args.removeSysfuncs
        self.takeallev = _args.takeallev
        self.debug = _args.debug

        self.recursiveParse = _args.recursiveParse

        if self.recursiveParse == False:
            self.removeSysfuncs = False

        if _args.printArgs:
            self.__printArgs()

    def __printArgs(self):
        print("////////////////// printing arguments /////////////////////")
        print("directory: " + self.directory)
        print("filename: " + self.filename)
        print("test: " + str(self.test))
        print("recursiveParse: " + str(self.recursiveParse))
        print("removeSysfuncs: " + str(self.removeSysfuncs))
        print("takeallev: " + str(self.takeallev))
        print("debug: " + str(self.debug))
        print("///////////////////////////////////////////////////////////", end='\n\n')

if __name__ == "__main__":
    args()


