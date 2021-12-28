'''
Copyright (c) 2021 Yuta Nakamura. All rights reserved.
'''
import sys
import pydotplus
from typing import Iterable 
import re

debug = False 
'''
class edge:
    def __init__(self, src: str, dst: str):
        self.__src = src
        self.__dst = dst
'''
class vertex:
    def __init__(self, name, insts, type = 'normal', color = 'white'):
        self.__name = name
        self.__insts = insts
        self.__oedges = dict() # only the out-edges are kept
        self.__iedges = dict() # only incoming edges are kept
        self.__color = color 
        self.__type = None

    def get_name(self):
        return self.__name

    def get_insts(self):
        return self.__insts

    def set_insts(self, insts: list) -> None:
        self.__insts = insts

    def get_type(self):
        return self.__type


    def append_oedge(self, dst):
        if dst.get_name() in self.__oedges:
            if debug:
                print("appended the same child twice for oedges: " + dst.get_name())
            assert dst == self.__oedges[dst.get_name()]
            return
        self.__oedges[dst.get_name()] = dst 
        return

    def del_oedge(self, oedge):
        if not oedge.get_name() in self.__oedges:
            # raise Exception('the oedge not found: ' + oedge.get_name())
            return 

        del self.__oedges[oedge.get_name()]
    
    def set_oedges(self, new_oedges: dict):
        self.__oedges = new_oedges

    def append_iedge(self, src):
        if src.get_name() in self.__iedges:
            if debug: 
                print("appended the same parent twice for iedges: " + src.get_name())
            assert src == self.__iedges[src.get_name()]
            return
        self.__iedges[src.get_name()] = src
        #self.__iedges.append(src) 
    
    def del_iedge(self, iedge):
        if not iedge.get_name() in self.__iedges:
            # raise Exception('the iedge not found: ' + iedge.get_name())
            return
        del self.__iedges[iedge.get_name()]

    def visit(self):
        self.__color = 'black'

    def is_visited(self):
        return self.__color == 'gray' or self.__color == 'black'

    def clear_visit(self):
        self.__color = 'white' 

    def get_children(self):
        return self.__oedges

    def set_type(self, _type: str):
        if _type != 'normal' and _type != 'end' and _type != 'root':
            raise Exception('wrong input in type!')
        self.__type = _type

    def has_mult_parent(self):
        return len(self.__iedges) > 1

    def get_parents(self):
        return self.__iedges

    def has_siblings(self):
        # need to know if one of the parent has multiple children
        for parent in self.__iedges:
            if len(self.__iedges[parent].get_children()) > 1:
                return True
        return False

    def siblings_are_parsed(self):
        for parent in self.__iedges:
            children = self.__iedges[parent].get_children()
            for child in children:
                if self.__name != children[child].get_name() and not children[child].is_visited():
                    return False

    def mv2bedges(self, oe): # oe is vertex here
        fnd = False
        if oe.get_name() in self.__oedges:
            fnd = True
            del self.__oedges[oe.get_name()]  
        if not fnd:
            raise Exception("edge not found: " + oe)
        
        assert self.__num_oedges >= 0
        self.__bedges[oe.get_name()] = oe
        assert len(self.__bedges) == self.__num_bedges
        assert len(self.__oedges) == self.__num_oedges

    def has_insts(self) -> bool:
        if len(self.__insts) == 0:
            return False
        return True
    def print_insts(self):
        for inst in self.__insts:
            print(inst[0] + '/' + str(inst[1]))
        
    def vprint(self):
        print('--------------------------------------------------------------------')
        print('name: ' + self.__name);
        print('insts:'); print(self.__insts)
        print('type: ' + self.__type)
        print('num_oedges: ', end = ''); print(len(self.__oedges))
        print('num_iedges: ', end = ''); print(len(self.__iedges))
        
        print('oedges: ', end = ''); # print(self.__oedges)
        for oedge in self.__oedges:
            print(oedge, end = ',')

        print('iedges: '); # print(self.__iedges)
        for iedge in self.__iedges:
            print(iedge, end = ',')

        print('color: ' + self.__color)
        print('--------------------------------------------------------------------')

    def fwrite_vertex(self, fp):
        fp.write('--------------------------------------------------------------------\n')
        fp.write('name: ' + self.__name); fp.write('\n')
        fp.write('insts:'); 
        for i in range(len(self.__insts)):
            fp.write(self.__insts[i][0])
            fp.write('/')
            fp.write(str(self.__insts[i][1]))
            if i < len(self.__insts) - 1:
                fp.write(':')
        fp.write('\n')
        fp.write('num_oedges: '); fp.write(str(self.__num_oedges)); fp.write('\n')
        fp.write('num_iedges: '); fp.write(str(self.__num_iedges)); fp.write('\n')
        
        fp.write('oedges: '); 
        for oedge in self.__oedges:
            fp.write(oedge); fp.write(',')
        fp.write('\n')

        fp.write('iedges: '); 
        for iedge in self.__iedges:
            fp.write(iedge); fp.write(',')
        fp.write('\n')

        fp.write('color: ' + self.__color); fp.write('\n')
        fp.write('--------------------------------------------------------------------\n')

    def out_result(self, fp):
        fp.write(self.__name + ',')
        for i in range(len(self.__insts)):
            fp.write(self.__insts[i][0])
            fp.write('/')
            fp.write(str(self.__insts[i][1]))
            if i < len(self.__insts) - 1:
                fp.write(':')
        if len(self.__insts) == 0:
            fp.write('na')
        fp.write(',')
        # this is the part that is being added
        fp.write(str(len(self.__iedges))); fp.write(',')

        oedges = self.__oedges 
        fp.write(str(len(oedges))); fp.write(',')
        '''
        if len(self.__iedges) <= 1 and len(oedges) <= 1 and len(self.__insts) == 0 and self.__type == 'normal':
            print(self.__name)
            print('iedge: ', end = '')
            print(self.__iedges)
            print('oedge: ', end = '')
            print(self.__oedges)
            raise Exception("this node should not be here")
        '''

        cnt = 0
        for iedge in self.__iedges:
            fp.write(iedge)
            if cnt < len(self.__iedges) - 1:
                fp.write(':')
            cnt += 1
        if len(self.__iedges) == 0:
            fp.write('na')
        fp.write(',')

        cnt = 0
        for oedge in oedges:
            fp.write(oedge)
            if cnt < len(oedges) - 1:
                fp.write(':')
            cnt += 1
        if len(oedges) == 0:
            fp.write('na')
        fp.write('\n')
       
class cfg:
    def __init__(self, name):
        self.name = name
        self.__vertices = dict() 
        self.__root = None
        self.__ends = list()
        # not gonna have edges as of now

    def create_entrypoint(self):
        old_root = self.__root
        insts = list()
        new_root = vertex('entrypoint', insts, 'root', 'white', True)
        old_root.set_type('normal')
        self.__root = new_root
        self.__vertices['entrypoint'] = self.__root
        
        return old_root, new_root

    def append_vertex(self, insts, n):
        if n.get_name() in self.__vertices:
            raise Exception('duplicate vertex: ' + n.get_name())
        real_name = self.__parse_name(n.get_name())
        self.__vertices[real_name] = vertex(real_name, insts)
    
    def remove_vertex(self, vName: str):
        del self.__vertices[vName]

    def append_edge(self, e):
        src = self.__parse_name(e.get_source())
        dst = self.__parse_name(e.get_destination())
        src_vx = self.__vertices[src]
        dst_vx = self.__vertices[dst]

        if src not in self.__vertices:
            raise Exception('src not found: ' + src)
        else: 
            src_vx.append_oedge(dst_vx)

        if dst not in self.__vertices:
            raise Exception('dst not found: ' + dst)
        else:
            dst_vx.append_iedge(src_vx)

    def get_root(self):
        if self.__root == None:
            self.__figure_root()
        return self.__root

    def get_vertices(self):
        return self.__vertices

    def get_vertices_topdown(self):
        rv = dict()
        self.clear_visit()
        root = self.__root
        if root == None:
            raise Exception("root not found")
        stack = list()
        stack.append(root)
        while len(stack) > 0:
            curr = stack.pop()
            if curr.is_visited():
                continue
            curr.visit()
            rv[curr.get_name()] = curr
            children = curr.get_children()
            for name, child in children.items():
                if not child.is_visited():
                    stack.append(child)
        self.clear_visit()
        return rv

    def set_root(self, new_root):
        self.__root = new_root

    def find_root(self):
        cand = list()
        for vName, v in self.__vertices.items():
            if len(v.get_parents()) == 0:
                cand.append(v)
            else:
                v.set_type('normal')
        if len(cand) != 1:
            raise Exception("multiple root found, there is something wrong with the cfg dotfile")
        self.__root = cand[0]
        cand[0].set_type('root')


    def get_node(self, name: str):
        return self.__vertices[name] 

    def clear_visit(self):
        for v in self.__vertices:
            self.__vertices[v].clear_visit()

    def set_types(self):
        # gonna find the leaves with dfs here
        root = self.get_root() 
        if root == None:
            raise Exception("root not found")
        if debug:
            print(root.get_name())
        self.clear_visit()
        visited_stack = dict()
        self.__DFSUtil(root, visited_stack.copy())
        self.clear_visit()
    
    def get_ends(self): # this is necessary to do the reverse post order
        if len(self.__ends) == 0:
            raise Exception("ends are not stored yet!")
        return self.__ends

    def get_end(self):
        rv = self.__get_end_traversal(self.__root)
        if rv != None:
            return rv
        else:
            raise Exception("error getting exception")
        
    def print_vertices(self):
        for v in self.__vertices:
            self.__vertices[v].vprint()

    def fwrite_vertices(self, ofile):
        f = open(ofile, 'w')
        self.clear_visit()
        stack = list()
        stack.append(self.__root)

        while len(stack) > 0:
            node = stack.pop()
            if node.is_visited():
                continue
            node.visit()
            node.fwrite_vertex(f)
            children = node.get_children() 
            if len(children) > 0:
                for child in children:
                    stack.append(children[child])

        f.close()
        self.clear_visit()
        return 
    
    def out_result(self, ofile):
        f = open(ofile, 'w')
        self.clear_visit()
        stack = list()
        stack.append(self.__root)
        while len(stack) > 0:
            node = stack.pop()
            if node.is_visited():
                continue
            node.visit()
            node.out_result(f)
            children = node.get_children()
            if len(children) > 0:
                for child in children:
                    stack.append(children[child])
        f.close()
        self.clear_visit()
    # helper function to parse the name into the right format
    def __parse_name(self, name):
        p = re.compile('Node(\w*)')
        m = p.match(name)
        if m == None:
            raise Exception('name not in the right format') 
        else:
            return m.group(1)
    
    def __figure_root(self):
        for v in self.__vertices:
            if self.__vertices[v].get_type() == "root":
                self.__root = self.__vertices[v] 
                return
            
    def __DFSUtil(self, node, visited_stack):
        node.visit()
        if debug:
            print(visited_stack)
        if node.get_name() in visited_stack:
            raise Exception('came to the same node twice')
        visited_stack[node.get_name()] = 1
        
        if debug:
            print('printing children')
            for child in node.get_children():
                print(child.get_name(), end = ',')
            print()

        oes = node.get_children().copy()
        for oe in oes:
            if oe in visited_stack: #if the edge leads to the place where it's visited 
                # you need to move this edge as a back edge
                if debug:
                    print('back edge found!:' + oe.get_name())
                node.mv2bedges(oes[oe]) 
            elif not oes[oe].is_visited():
                self.__DFSUtil(oes[oe], visited_stack.copy())
                
        if len(node.get_children()) == 0:
            node.set_type('end')
            self.__ends.append(node)
            
    def __get_end_traversal(self, node):
        node.visit()
        for name, child in node.get_children().items():
            if not child.is_visited():
                rv = self.__get_end_traversal(child)
                if rv != None:
                    return rv
        if len(node.get_children()) == 0:
            return node
        return None
        

def parse_attributes(n):
    insts = n.get_attributes()['label'][2:-2].split('\l')
    for i in range(len(insts)):
        insts[i] = insts[i].lstrip('\t ') 
    return insts

def parse_dot(filename: str, cfg_dict: dict, infos: dict) -> (cfg, bool):
    graph = pydotplus.graph_from_dot_file(filename)
    if graph == None:
        raise Exception('graph_from_dot_file not worked properly: ' + filename)
    cfg_name = graph.get_name()
    rv = cfg(cfg_name)
    if cfg_name in cfg_dict:
        return cfg_dict[cfg_name], True 
    cfg_dict[cfg_name] = None 
    nodeList = graph.get_node_list() 
    infos["blocks"] += len(nodeList)
    # print(filename + ':' + str(len(nodeList)))

    for n in nodeList:
        insts = parse_attributes(n)
        rv.append_vertex(insts, n)

    edgeList = graph.get_edge_list()
    infos["edges"] += len(edgeList)

    for e in edgeList:
        rv.append_edge(e)
    
    rv.find_root()

    return rv, False

def create_empty_vertex(name: str):
    rv = vertex(name, list())
    return rv

if __name__ == "__main__":
    assert len(sys.argv) == 2
    filename = sys.argv[1]
    cfg_, flag = parse_dot(filename)

