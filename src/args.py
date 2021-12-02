# to do: I want to make recursiveParse default to true

import argparse

class args:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument("directory", type=str, help="directory name") 
        parser.add_argument("filename", nargs='?', type=str, help="file to parse", default='main')
        parser.add_argument("-t", "--test", action="store_true")
        parser.add_argument("-s", "--removeSysfuncs", action="store_true")
        parser.add_argument("-e", "--takeallev", action="store_true")
        parser.add_argument("-d", "--debug", action="store_true")
        parser.add_argument("-p", "--printArgs", action="store_true")
        parser.add_argument("-r", "--recursiveParse", nargs='?', default=True, type=bool, action="store", help="either to recursively parse all the functions")

        _args = parser.parse_args()

        self.directory = _args.directory
        self.filename = _args.filename

        self.test = _args.test
        self.removeSysfuncs = _args.removeSysfuncs
        self.takeallev = _args.takeallev
        self.debug = _args.debug

        self.recursiveParse = _args.recursiveParse

        if _args.printArgs:
            self.__printArgs()

    def __printArgs(self):
        print(self.directory + '/' + self.filename)
        if self.test:
            print('testing the functions')
        if self.recursiveParse:
            print('recursiveParse')
        if self.removeSysfuncs:
            print('removeSysfuncs')
        if self.takeallev:
            print('takeallev')
        if self.debug:
            print('debug')

if __name__ == "__main__":
    args()


