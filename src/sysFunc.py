
# todo: find a way to take away the redundancy of find_syscall and find_specsyscall
class RemoveSysFuncs:

    def __init__(self):
        pass

    def removeSysFuncs(self, data: dict, _file: str, tmpCFG_dict: dict, func_dict: dict):
        # don't worry about these for now
        syscall_dict = dict()
        # this function just finds whether the function includes the syscall or not
        self.find_syscall(tmpCFG_dict[_file], syscall_dict, tmpCFG_dict, func_dict)
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

        if name == 'cgt_init':
            print('at cgt_init:' + str(found))  
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
            if name == 'cgt_init':
                print(func + ',' + str(syscall_dict[func]))

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

