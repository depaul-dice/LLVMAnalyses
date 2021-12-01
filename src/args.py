
import argparse

class args:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument("directory", type=str, help="directory name") 
        parser.add_argument("filename", nargs='?', type=str, help="file to parse", default='main')
        parser.add_argument("-t", "--test", action="store_true")
        parser.add_argument("-r", "--recursiveParse", action="store_true")
        parser.add_argument("-s", "--removeSysfuncs", action="store_true")
        parser.add_argument("-e", "--takeallev", action="store_true")
        parser.add_argument("-d", "--debug", action="store_true")
        parser.add_argument("-p", "--printArgs", action="store_true")
       
        _args = parser.parse_args()
        self.test = _args.test
        self.recursiveParse = _args.recursiveParse
        self.removeSysfuncs = _args.removeSysfuncs
        self.takeallev = _args.takeallev
        self.debug = _args.debug


        if _args.printArgs:
            print(_args.directory + '/' + _args.filename)
            if _args.test:
                print('testing the functions')
            if _args.recursiveParse:
                print('recursiveParse')
            if _args.removeSysfuncs:
                print('removeSysfuncs')
            if _args.takeallev:
                print('takeallev')
            if _args.debug:
                print('debug')


if __name__ == "__main__":
    args()


