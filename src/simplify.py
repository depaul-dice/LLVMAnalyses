# todo: let's make this into a class so that you can shove some simplifying classes here too

import pdb
from CONSTANTS import badFuncs, TAKEOUTSYSCALLS

# todo: find a way to take away the redundancy of find_syscall and find_specsyscall
class RemoveSysFuncs:

    def __init__(self):
        pass

    def removeSysFuncs(self, data: dict, _file: str, tmpCFG_dict: dict, func_dict: dict):
        # don't worry about these for now
        syscall_dict = dict()
        # this function just finds whether the function includes the syscall or not
        self.find_syscall(tmpCFG_dict[_file], syscall_dict, tmpCFG_dict, func_dict)

        self.findNoneSyscallDict(syscall_dict, tmpCFG_dict, func_dict) 

        # below is the sys file
        self.writeSyscallDict(syscall_dict, "syscall.txt")

        for funcName, necessary in syscall_dict.items():
            if necessary:
                data["necessaryFuncs"] += 1

        # this function finds which function has what
        specSyscallDict = dict()
        self.find_specSyscall(tmpCFG_dict[_file], specSyscallDict, tmpCFG_dict, func_dict)
        
        for funcName, necessary in syscall_dict.items():
            if not necessary:
               del tmpCFG_dict[funcName] 

        unnec_insts = 0
        for name, _cfg in tmpCFG_dict.items():
            unnec_insts += self.deleteUnnecessaryFuncs(_cfg, syscall_dict, func_dict)
        data["relevant"] = data["semiRelevant"] - unnec_insts

    def getFuncsFromCFGs(self, cfg) -> list:
        cfg.clear_visit()
        stack = list()
        stack.append(cfg.get_root())
        funcList = list()
        while len(stack) > 0:
            curr = stack.pop()
            if curr.is_visited():
                continue
            curr.visit()
            insts = curr.get_insts()
            for inst in insts:
                if inst[0] != 'syscall' and inst[0] != 'ret':
                    funcList.append(inst[0])
            children = curr.get_children()
            for child_name, child in children.items():
                if not child.is_visited():
                    stack.append(child)
        cfg.clear_visit()
        return funcList
            
    def findNoneSyscallDict(self, syscall_dict: dict, cfgs: dict, func_dict: dict) -> None:
        for funcName, cfg in cfgs.items():
            assert funcName in syscall_dict
            if syscall_dict[funcName] == None:
                funcList = self.getFuncsFromCFGs(cfg)
                for func in funcList:
                    if syscall_dict[func] == True:
                        syscall_dict[funcName] = True
                if syscall_dict[funcName] == None:
                    syscall_dict[funcName] = False
        
    def find_syscall(self, cfg, syscall_dict: dict, tmpCFG_dict: dict, func_dict: dict) -> dict:
        # renaming the cfg 
        name = cfg.name
        if name in func_dict:
            name = func_dict[name]
            cfg.set_name(name)
        syscall_dict[name] = None 
        
        # traversing in a bfs way
        cfg.clear_visit()
        stack = list()
        stack.append(cfg.get_root())
        found = False
        funcList = list()
        while len(stack) > 0:
            curr = stack.pop()
            if curr.is_visited():
                continue
            curr.visit()
            insts = curr.get_insts()
            for inst in insts:
                # print(inst)
                if inst[0] == 'syscall':
                    found = True
                elif inst[0] != 'ret':
                    if inst[0] in func_dict:
                        inst = (func_dict[inst[0]], inst[1]) # this might now have changed as the way i wanted 
                    funcList.append(inst[0]) # adding the ones to inspect
            children = curr.get_children()
            for child_name, child in children.items():
                if not child.is_visited():
                    stack.append(child)
        cfg.clear_visit()

        for func in funcList:
            if func not in syscall_dict:
                self.find_syscall(tmpCFG_dict[func], syscall_dict, tmpCFG_dict, func_dict)
            if found == False and syscall_dict[func] == True:
                found = True
            elif found == False and syscall_dict[func] == None:
                print(func + " is recursive")
                found = None
            elif found == None and syscall_dict[func] == True:
                print("resolving recursion for " + func)
                found = True

        syscall_dict[name] = found
        return syscall_dict 
     
    def writeSyscallDict(self, syscall_dict, filename):
        with open(filename, "w") as f:
            for key, value in syscall_dict.items():
                f.write(key + ':' + str(value) + '\n')

    # this function has which function has what
    def find_specSyscall(self, cfg, specSyscallDict: dict, tmpCFG_dict: dict, func_dict: dict) -> dict:
        name = cfg.name
        if name in func_dict:
            name = func_dict[name] 
            cfg.set_name(name)
        specSyscallDict[name] = None
        #print("specSys, adding " + name)

        cfg.clear_visit()
        stack = list()
        stack.append(cfg.get_root())
        funcList = list()
        rv = dict()
        while len(stack) > 0:
            curr = stack.pop()
            if curr.is_visited():
                continue
            curr.visit()
            insts = curr.get_insts()
            for inst in insts:
                if inst[0] == 'syscall':
                    rv[inst[1]] = 1 
                elif inst[0] != 'ret':
                    #print("specSys, found " + inst[0])
                    if inst[0] in func_dict:
                        inst = (func_dict[inst[0]], inst[1])
                    funcList.append(inst[0])
            children = curr.get_children()
            for child_name, child in children.items():
                if not child.is_visited():
                    stack.append(child)
        cfg.clear_visit()

        for func in funcList:
            if func not in specSyscallDict:
                tmp = self.find_specSyscall(tmpCFG_dict[func], specSyscallDict, tmpCFG_dict, func_dict)
                rv.update(tmp)    
        specSyscallDict[name] = rv 
        return rv

    def deleteUnnecessaryFuncs(self, cfg, syscall_dict: dict, func_dict: dict) -> int:
        cfg.clear_visit()
        stack = list()
        stack.append(cfg.get_root())
        rv = 0
        while len(stack) > 0:
            curr = stack.pop()
            if curr.is_visited():
                continue
            curr.visit()
            insts = curr.get_insts()
            old = insts.copy()
            
            index = 0
            tmpList = list()
            for inst in insts:
                if inst[0] != 'ret' and inst[0] != 'syscall':
                    if inst[0] in func_dict: 
                        func = func_dict[inst[0]]
                    else:
                        func = inst[0]
                    if not syscall_dict[func]:
                        tmpList.append(index)
                index += 1

            rv += len(tmpList)
            while len(tmpList) > 0:
                element = tmpList.pop()
                insts.pop(element)
            curr.set_insts(insts)

            children = curr.get_children()
            for child_name, child in children.items():
                if not child.is_visited():
                    stack.append(child)
        cfg.clear_visit()

        return rv 

class nodeRemoval:
    def __init__(self):
        pass

    def __dfs_visit(self, curr, vertices:dict) -> None:
        if curr.is_visited():
            return
        curr.visit()
        if not curr.has_insts():
            vertices[curr.get_name()] = curr

        for name, child in curr.get_children().items():
            self.__dfs_visit(child, vertices)
        return

    def list_vertices(self, cfg) -> dict:
        rv = dict()
        root = cfg.get_root()
        cfg.clear_visit()
        self.__dfs_visit(root, rv)
        cfg.clear_visit()
        return rv

    def create_bipartite_graph(self, curr, Vs: dict) -> None:
        if curr.get_type() == 'root':
            return
        srcs = curr.get_parents()
        dests = curr.get_children()
        if len(srcs) == 0:
            raise Exception("the vertex should have the incoming edges unless root")

        if curr.get_name() in srcs:
            assert curr.get_name() in dests
            curr.del_oedge(curr)
            curr.del_iedge(curr)

        # first delete all curr from all the srcs and dests 
        for src_name, src in srcs.items():
            src.del_oedge(curr)
            
        for dst_name, dst in dests.items():
            dst.del_iedge(curr)

        del Vs[curr.get_name()]
        # if there is no outgoing edges, you dont have to iterate through
        if len(dests) == 0:
            return

        # then for each src, add each dest as an oedge 
        # also for each dest, add each src as an iedge
        for name_src, src in srcs.items():
            for name_dest, dest in dests.items():
                src.append_oedge(dest)
                dest.append_iedge(src)

    def delete_emptyNodes(self, emptyVertices: dict, cfg):
        Vs = cfg.get_vertices()
        for eName, eV in emptyVertices.items():
            self.create_bipartite_graph(eV, Vs)

    def delete_redundantNodes(self, emptyVertices: dict, cfg):
        # print(cfg.name)
        flag = True
        cnt = 0
        Vs = cfg.get_vertices()
        while flag:
            flag = False

            cnt += 1
            # print("cnt %d"%cnt)
            currVertices = emptyVertices.copy()
            for eName, eV in currVertices.items():
                # if it has a self loop, delete
                
                if eV.get_type() == 'root':
                    continue
                srcs = eV.get_parents()
                dsts = eV.get_children()
                if eName in srcs:
                    del srcs[eName]
                    assert eName in dsts
                    del dsts[eName]
                    flag = True

                srcs = eV.get_parents()
                dsts = eV.get_children()
                if len(srcs) <= 1 and len(dsts) <= 1:
                    # delete the eName from src and dst 
                    # print("deleting %s"%eName)
                    sName = None
                    src = None
                    srcC = None

                    if len(srcs) == 1:
                        src = next(iter(srcs.values()))
                        sName = src.get_name()
                        srcC = src.get_children()
                        del srcC[eName]

                    if len(dsts) == 1:
                        dst = next(iter(dsts.values()))
                        dName = dst.get_name()
                        dstP = dst.get_parents()
                        del dstP[eName]

                        if len(srcs) == 1:
                            srcC[dName] = dst
                            dstP[sName] = src
                        
                    del emptyVertices[eName]
                    del Vs[eName] 
                    flag = True
        return

    def __count_nodes(self, curr):
        if curr.is_visited():
            return 0, 0
        curr.visit()
        vcount, ecount = 1, 0 
        for name, child in curr.get_children().items():
            ecount += 1
            tmp_vcount, tmp_ecount = self.__count_nodes(child)
            vcount += tmp_vcount; ecount += tmp_ecount
        return vcount, ecount 

    def count_vertices(self, cfg):
        rv = self.__count_nodes(cfg.get_root())
        cfg.clear_visit()
        return rv

    def printEV(self, empty_vertices):
        for empty_name, empty_v in empty_vertices.items():
            print(empty_name, end = ',')
            print(len(empty_v.get_parents()), end = ',')
            print(len(empty_v.get_children()), end = ':')
        print()

    def __takeOutSyscallInsts(self, curr):
        if curr.is_visited():
            return
        curr.visit()
        insts = curr.get_insts()
        _len = len(insts)
        for i in reversed(range(_len)):
            if insts[i][0] == "syscall":
                tmp = insts.pop(i)
            elif insts[i][0] in badFuncs:
                print("found!: " + insts[i][0])
                tmp = insts.pop(i)

        for name, child in curr.get_children().items():
            self.__takeOutSyscallInsts(child)
        return

    def takeOutSyscallInsts(self, cfg) -> None:
        root = cfg.get_root()
        cfg.clear_visit()
        self.__takeOutSyscallInsts(root)
        cfg.clear_visit()
        return 

    def run(self, cfg, allEV: bool):
        '''
        what to do
        (0. you take out the syscalls)
        1. list all the vertices that are empty
        2. create a bipartite graph for all of the edges that are empty
        '''
        if TAKEOUTSYSCALLS:
            self.takeOutSyscallInsts(cfg)
        empty_vertices = self.list_vertices(cfg)

        if allEV:
            self.delete_emptyNodes(empty_vertices, cfg)
        else:
            self.delete_redundantNodes(empty_vertices, cfg)
        
        vcount, ecount = self.count_vertices(cfg)
        
        return vcount, ecount

