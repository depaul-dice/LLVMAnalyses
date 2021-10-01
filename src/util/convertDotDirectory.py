import os
import sys

class edge:
    def __init__(self, src: str, dst: str):
        self.src = src
        self.dst = dst
    def __str__(self):
        return self.src + ' -> ' + self.dst
        
class node:
    def __init__(self, name: str, type: str, sysnum: int, funcName: str):
        self.name = name
        self.type = type
        self.sysnum = sysnum
        self.funcName = funcName

    def __str__(self):
        rv = self.name + ',' + self.type 
        if self.type == "syscall":
            rv += ',' + str(self.sysnum)
        elif self.type == "funccall":
            rv += ',' + self.funcName
        return rv

class cfg:
    def __init__(self, path: str):
        if not os.path.exists(path):
            raise Exception("the path: " + path + " does not exist!")
        self.name = path[path.rfind('/') + 1: path.rfind('.')] 
        self.edges = list()
        self.nodes = list()
        self.readFile(path)

    def readFile(self, path):
        with open(path, "r") as f:
            for line in f:
                infos = line[:-1].split(',')
                name = infos[0]
                type = infos[1]
                index = 2
                sysnum = -1
                funcname = None
                if type == 'syscall':
                    sysnum = infos[index]
                    index += 1
                elif type == 'funccall':
                    funcname = infos[index]
                    index += 1
                elif type == 'ret' or type == 'epoint' or type == 'empty':
                    pass 
                else:
                    raise Exception("type not known: " + type)

                self.nodes.append(node(name, type, sysnum, funcname))
                numOedges = int(infos[index]); index += 1
                numIedges = int(infos[index]); index += 1
                numBedges = int(infos[index]); index += 1
                if infos[index] != 'na':
                    oedges = infos[index].split(':'); index += 1
                else:
                    oedges = None; index += 1

                if infos[index] != 'na':
                    iedges = infos[index].split(':'); index += 1
                else:
                    iedges = None; index += 1
                
                if infos[index] != 'na':
                    bedges = infos[index].split(':')
                else:
                    bedges = None

                if numOedges + numBedges > 1:
                    index = 0
                    if oedges != None:
                        for i in range(len(oedges)):
                            self.edges.append(edge(name + ':s' + str(i), oedges[i]))
                            index += 1
                    if bedges != None:
                        for i in range(len(bedges)):
                            self.edges.append(edge(name + ':s' + str(index), bedges[i]))
                            index += 1
                    
                else:
                    if numOedges == 1:
                        self.edges.append(edge(name, oedges[0]))
                    if numBedges == 1:
                        self.edges.append(edge(name, bedges[0]))
                
    def print(self):
        for node in self.nodes:
            print(node)
        for edge in self.edges:
            print(edge)

    def createDotFile(self, outPath):
        with open(outPath, 'w') as f:
            f.write('digraph \"' + self.name 
                    + '\" {\n\tlabel=\"' + self.name + '\";\n\n')
            for node in self.nodes: 
                if node.type == 'syscall':
                    f.write('\tNode' + node.name 
                            + ' [shape=record, label=\"{' + node.name + '\l'
                            + node.type + '\l'
                            + node.sysnum 
                            + '\l}\"];\n')
                elif node.type == 'funccall':
                    f.write('\tNode' + node.name 
                            + ' [shape=record, label=\"{' + node.name + '\l'
                            + node.type + '\l'
                            + node.funcName
                            + '\l}\"];\n')
                else:
                    f.write('\tNode' + node.name 
                            + ' [shape=record, label=\"{' + node.name + '\l'
                            + node.type
                            + '\l}\"];\n')

            for edge in self.edges:
                f.write('\tNode' + edge.src + ' -> Node' + edge.dst + ';\n')
            f.write('}')
                       

def main():
    if len(sys.argv) != 3:
        print("usage: python3 convertDot.py /path/to/parsed/directory /output/file/directory")
        return 
    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    for filename in os.listdir(input_directory): 
        g = cfg(os.path.join(input_directory, filename))
        # g.print()
        if filename.rfind('.') != -1:
            g.createDotFile(os.path.join(output_directory, filename[:filename.rfind('.')] + '.dot'))
        else:
            g.createDotFile(os.path.join(output_directory, filename, '.dot'))

if __name__ == "__main__":
    main()
