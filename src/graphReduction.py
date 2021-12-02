import parseDot 
import tools 
from simplify import further_simplify
from oneInstG import oneInstG_t
import tests
import sys
import re
import os
import shutil
from args import args

Args = args() 
'''
Args.test = True 

Args.debug = False 
Args.takeallev = True 

Args.recursiveParse = True
Args.removeSysfuncs = True
'''

cfg_dict = dict()
notFound_dict = dict()

func_dict = {
       '__libc_exit_fini' :'libc_exit_fini',
        'fdopen': '__fdopen',
        '___errno_location': '__errno_location',
        'ofl_lock': '__ofl_lock',
        '__isoc99_sscanf': 'sscanf',
        # '__lctrans_impl': '__lctrans', this was so wrong, they were two different funcs
        '_IO_getc': 'getc',
        '_IO_putc': 'putc',
        'lstat64': 'lstat',
        'stat64': 'stat',
        'open64': 'open',
        'lseek64': 'lseek',
        'readdir64': 'readdir',
        'fstat64': 'fstat',
        'pthread_mutex_lock': '__pthread_mutex_lock',
        'pthread_mutex_unlock': '__pthread_mutex_unlock',
        'pthread_create': '__pthread_create',
        'pthread_once': '__pthread_once',
        'pthread_cond_timedwait': '__pthread_cond_timedwait',
        'pthread_key_create': '__pthread_key_create',
        'pthread_getspecific': '__pthread_getspecific',
        'pthread_rwlock_trywrlock': '__pthread_rwlock_trywrlock', 
        'pthread_join':'__pthread_join',
        'clock_gettime': '__clock_gettime',
        'crc32': 'crc32z',
        'adler32': 'adler32z',
        }

unnec = {
        '__funcs_on_exit': 1,
        'mal': 1,
        'net': 1, 
        '__abort_lock': 1,
        '_fini': 1,
        'all_mask': 1,
        'main.bonus': 1,
        'progNameReally': 1,
        'outName': 1,
        'inName': 1,
        'tmpName': 1,
        'fileMetaInfo': 1,
        '__stderr_FILE': 1,
        '__stdout_FILE': 1,
        '__stdin_FILE': 1,
        }

syscall_patterns = [ 
        r'%\d+\s=\stail\scall\si64\s@__syscall_cp\(i64\s(\d+),',
        r'%\d+\s=\stail\scall\sfastcc\si64\s@__syscall_cp\(i64\s(\d+),',
        r"%\d+\s=\scall\si64\s@__syscall_cp\(i64\s(\d+),",
        r"%\d+\s=\scall\sfastcc\si64\s@__syscall_cp\(i64\s(\d+),",
        r'syscall,\s=\\\{ax\\\},\\\{ax\\\},[^\(]*\}\s?[\s\(]\s?i64\s(\d+)',
        r'syscall,\s=\\\{ax\\\},\\\{ax\\\},\\\{di\\\},\\\{si\\\},~\\\{rcx\\\},~\\\{r11\\\},~\\\{memory\\\},~\\\{dirflag\\\},~\\\{fpsr\\\},~\\\{flags\\\}\(i64\s(\d+)'
        ]

def find_syscalls(inst: str) -> (list, int):
    if inst.find('syscall') == -1:
        return None
    for pattern in syscall_patterns:
        p = re.compile(pattern)
        m = re.findall(p, inst)
        if len(m) > 0:
            if len(m) >= 2:
                raise Exception("syscall found twice in the instruction")
            return ['syscall'], int(m[0])
    if inst.find('__syscall_ret') == -1:
        raise Exception(inst + ': this could not be parsed')
    return None

def inst2keep(inst: str, bitcasts: dict) -> (list, int):
    bitcast_pattern = r'(%\d+)\s=\sbitcast\s.*%struct\._IO_FILE\.\d+.*\s@(\w*)\sto\s(.+)'
    ret_pattern = r'^ret\s'
    func_pattern = r'\s*call\s+' # changed this to + from *
    fname_pattern = r'@([A-Za-z0-9_][\w_]*([.?]\w*|))\('
    bitcastResolve_pattern = r'%\d+\s=\s(tail\s|)call\s(%struct._IO_FILE|)(i\d+|)\*?\s(%\d+)\('

    #p = re.compile(ret_pattern) 
    m = re.findall(ret_pattern, inst)
    if len(m) > 0:
        return ['ret'], -1
    m = re.search(bitcast_pattern, inst)
    if m:
        # print(m.group(1) + ':' + m.group(2) + ':' + m.group(3))
        if m.group(1) in bitcasts:
            raise Exception(m.group(1) + " already in bitcasts, " + m.group(2) + " vs. " + bitcasts[m.group(1)])
        bitcasts[m.group(1)] = m.group(2)

        return None

    m = re.findall(func_pattern, inst)
    rv = list() 
    flag = False
    if len(m) > 0:
        syscalls = find_syscalls(inst)
        if syscalls != None:
            return syscalls 
        p = re.compile(fname_pattern)
        matches = p.finditer(inst)
        for match in matches:
            funcname = inst[match.start() + 1:match.end() - 1]
            if funcname.find('llvm.') != -1 or funcname.find('__syscall_ret') != -1 or funcname.find('__vm_wait') != -1 or funcname.find('expand_heap.') != -1 or funcname.find('__PRETTY_FUNCTION__.') != -1 or funcname in unnec:
                flag = True
                continue
            if funcname.find('__syscall_cp') != -1:
                print(inst)
                raise Exception('__syscall_cp not caught')
            rv.append(funcname)
        if len(rv) == 0 and flag == False:
            # see if it's resolvable

            n = re.search(bitcastResolve_pattern, inst)
            if n:
                # print("found: %s, %s"%(inst, n.group(4)))
                if n.group(4) in bitcasts: 
                    rv.append(bitcasts[n.group(4)])
                    del bitcasts[n.group(4)]
                else: 
                    print("key error found: " + inst, file = sys.stderr)
            else:
                # print("WARNING: %s"%inst, file=sys.stderr)
                pass
                
            #raise Exception("Call found but could not get the function name: %s"%(inst))
        if len(rv) > 0:
            return rv, -1
        else:
            return None 
     
    return None

def not_line(inst: str) -> bool:
    pattern = re.compile(r'^\.\.\.')
    matches = pattern.finditer(inst)
    rv = sum(1 for _ in matches)
    if rv > 0:
        return True
    elif rv == 0:
        return False
    else:
        raise Exception('no negative values allowed')

def parse_block(block, directory: str, bitcasts: dict, infos: dict) -> None:
    old_insts = block.get_insts()
    infos["allInsts"] += len(old_insts)
    new_insts = list()
    concat_flag = False
    while len(old_insts) > 0:
        if concat_flag:
            tmp = old_insts.pop(0)
            if inst[-1] == ' ':
                inst = tmp
            else:
                inst += (' ' + tmp) 
            concat_flag = False
        else:
            inst = old_insts.pop(0)
        if len(old_insts) > 0 and not_line(old_insts[0]):
            old_insts[0] = old_insts[0][4:]
            concat_flag = True
            continue
        # print('new inst: ' + inst)
        parsed = inst2keep(inst, bitcasts)
        if parsed != None: # condition is met
            # then insert the inst at the very top
            funcs, num = parsed
            for func in funcs: 
                if func != 'syscall' and func != 'ret':
                    func_flag = False 
                    filename = func + '.dot' 
                    if func == '__syscall_ret' or parsed == '__syscall_cp':
                        raise Exception('didn\'t catch __syscall_cp or __syscall_ret')
                    if not os.path.exists(os.path.join(directory, filename)):
                        if func in func_dict:
                            tmpfunc = func_dict[func]
                            filename = tmpfunc + '.dot'
                            # print('translating: ' + filename)
                        else:
                            if func not in notFound_dict:
                                print("%s not found"%func)
                                notFound_dict[func] = 1
                                func_flag = True
                            continue
                            # raise Exception('file not found: %s'%filename)

                    if Args.recursiveParse:
                        parse_cfg(directory, filename, infos)
                new_insts.append((func, num)) 
    block.set_insts(new_insts)
    infos["semiRelevant"] += len(new_insts)
    return

def parse_func_topdown(cfg_, directory: str, infos: dict) -> None:
    vertices = cfg_.get_vertices()
    bitcasts = dict()
    for vName, vertex in vertices.items():
        parse_block(vertex, directory, bitcasts, infos)
    if len(bitcasts) != 0:
        # print(bitcasts, file = sys.stderr)
        # raise Exception(cfg_.name)
        pass

# this function has which function has what
def find_specSyscall(cfg, specSyscallDict, tmpCFG_dict) -> dict:
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
            tmp = find_specSyscall(tmpCFG_dict[func], specSyscallDict, tmpCFG_dict)
            rv.update(tmp)    
    specSyscallDict[name] = rv 
    return rv

def find_syscall(cfg, syscall_dict, tmpCFG_dict) -> dict:
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
            find_syscall(tmpCFG_dict[func], syscall_dict, tmpCFG_dict)
        if found == False and syscall_dict[func] == True:
            found = True

    syscall_dict[name] = found
    return syscall_dict 
            
def parse_func(cfg_, directory: str) -> None:
    cfg_.clear_visit()
    stack = cfg_.get_ends() # this is a list of vertices

    while len(stack) > 0:
        curr = stack.pop()

        if curr.is_visited():
            continue

        parse_block(curr, directory)
        curr.visit()
        parents = curr.get_parents()
        if curr.has_mult_parent(): # if curr has multiple parent
            for parent in parents:
                if not parents[parent].is_visited():
                    stack.append(parents[parent])

        elif curr.has_siblings():
            if curr.siblings_are_parsed(): 
                # merge var_list here
                # push the parent here
                for parent in parents:
                    if not parents[parent].is_visited():
                        stack.append(parents[parent])
                    
            # if not just let it be
        else: 
            # push the parent here
            parents = curr.get_parents()
            assert len(parents) == 0 or len(parents) == 1
            for parent in parents:
                stack.append(parents[parent])
    cfg_.clear_visit()
    return

def parse_cfg(directory: str, filename: str, infos: dict):
    path = os.path.join(directory, filename) 
    if not os.path.exists(path):
        raise Exception(path + " does not exist, exitting...")
    
    _cfg, flag = parseDot.parse_dot(path, cfg_dict, infos)
    if flag:
        return _cfg
    
    parse_func_topdown(_cfg, directory, infos)
    
    # I want to count the number of vertices and edges here (before simplification)
    
    if _cfg.name in cfg_dict and cfg_dict[_cfg.name] != None:
        raise Exception('this should be new cfg')
    elif not _cfg.name in cfg_dict:
        raise Exception(_cfg.name + ' should be in the dict')
    else:
        cfg_dict[_cfg.name] = _cfg
    infos["funcs"] += 1
    return _cfg

def parseCFGName(name: str) -> str:
    pattern = r'\"CFG\ for\ \'([\w\.]+)\'\ function\"'
    
    p = re.compile(pattern)
    m = re.match(p, name)
    if m == None:
        print(name)
        sys.exit(1)
    return m.group(1) 

def deleteUnnecessaryFuncs(cfg, syscall_dict: dict) -> int:
    
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

def countBranchMerge(cfg) -> (int, int):
    cfg.clear_visit()
    stack = list()
    stack.append(cfg.get_root())
    branch = 0
    merge = 0
    while len(stack) > 0:
        curr = stack.pop()
        if curr.is_visited():
            continue
        curr.visit()

        children = curr.get_children()
        if len(children) > 1:
            branch += 1
        if len(curr.get_parents()) > 1:
            merge += 1

        for child_name, child in children.items():
            if not child.is_visited():
                stack.append(child)
    cfg.clear_visit()
    return branch, merge

def __countBackEdgeRecursive(history: dict, currNode, backEdgeDsts: dict) -> int:
    backEdge = 0
    if currNode.is_visited():
        return backEdge
    currNode.visit()
    oEdges = currNode.get_children()
    for name, oEdge in oEdges.items():
        if name in history:
            if name not in backEdgeDsts:
                backEdge += 1
                backEdgeDsts[name] = 1
        else:
            histCopy = history.copy()
            histCopy[name] = oEdge
            backEdge += __countBackEdgeRecursive(histCopy, oEdge, backEdgeDsts)
    return backEdge

def countBackEdge(cfg) -> int:
    cfg.clear_visit()
    entryPoint = cfg.get_root()
    history = dict()
    backEdgeDsts = dict()
    backedge = __countBackEdgeRecursive(history, entryPoint, backEdgeDsts)
    cfg.clear_visit()
    return backedge
 
def writeSyscallDict(syscall_dict, filename):
    with open(filename, "w") as f:
        for key, value in syscall_dict.items():
            f.write(key + ':' + str(value) + '\n')

def graphReduction():
    # keep track of data reduction progress
    data = {
            "blocks": 0,
            "branchingBlocks": 0,
            "mergingBlocks": 0,
            "necessaryBlocks": 0,
            "necessaryBranchingBlocks": 0,
            "necessaryMergingBlocks": 0,
            "edges": 0,
            "necessaryEdges": 0,
            "backEdges": 0,
            "necessaryBackEdges": 0,
            "allInsts": 0,
            "semiRelevant": 0,
            "relevant": 0,
            "funcs": 0,
            "necessaryFuncs": 0,
            "finalNodes": 0,
            }
    
    # assert len(sys.argv) == 2 or len(sys.argv) == 3
    directory = Args.directory 
    filename = Args.filename + ".dot"
    _file = Args.filename

    # deleting tmp
    if Args.debug:
        try:
            os.mkdir("tmp")
        except (FileExistsError):
            shutil.rmtree("tmp")
            os.mkdir("tmp")
            print("tmp already exists, so I deleted and remade it")

    # deleting directory outs
    try:
        os.mkdir('outs')
    except FileExistsError:
        shutil.rmtree('outs')
        os.mkdir('outs')
        print("outs already existed, so I deleted and remade it", file = sys.stderr)
        
    # reading files and pruning unnecessary instructions
    _cfg = parse_cfg(directory, filename, data)
    
    old_names = list()
    tmpCFG_dict = dict()
    for name, _cfg in cfg_dict.items():
        old_names.append(name)
        name = parseCFGName(name) 
        # go through cfg and find if there's a syscall in them
        tmpCFG_dict[name] = _cfg
        _cfg.name = name

    for name, _cfg in cfg_dict.items():
        tmpBranch, tmpMerge = countBranchMerge(_cfg)
        data["branchingBlocks"] += tmpBranch
        data["mergingBlocks"] += tmpMerge
        data["backEdges"] += countBackEdge(_cfg)

    # don't worry about these for now
    syscall_dict = dict()
    # this function just finds whether the function includes the syscall or not
    find_syscall(tmpCFG_dict[_file], syscall_dict, tmpCFG_dict)
    # below is the sys file
    writeSyscallDict(syscall_dict, "syscall.txt")

    for funcName, necessary in syscall_dict.items():
        if necessary:
            data["necessaryFuncs"] += 1

    # this function finds which function has what
    specSyscallDict = dict()
    find_specSyscall(tmpCFG_dict[_file], specSyscallDict, tmpCFG_dict)
    
    for funcName, necessary in syscall_dict.items():
        if not necessary:
           del tmpCFG_dict[funcName] 

    unnec_insts = 0
    for name, _cfg in tmpCFG_dict.items():
        unnec_insts += deleteUnnecessaryFuncs(_cfg, syscall_dict)
    data["relevant"] = data["semiRelevant"] - unnec_insts
    
    blockNum = 0
    edgeNum = 0
 
    for name, _cfg in tmpCFG_dict.items():
        if Args.test:
            _tests = tests.cfgTests(_cfg)
            _tests.nodeCorrespondenceTest()

        # this function omits all the unnecessary vertices
        tmpBlockNum, tmpEdgeNum = further_simplify(_cfg, Args.takeallev)
        if Args.debug:
            outfile = 'tmp/' + _cfg.name + '.out'
            _cfg.out_result(outfile)
 
        blockNum += tmpBlockNum
        edgeNum += tmpEdgeNum

        # this is just checking if the procedure is done correctly 
        if Args.test:
            _tests = tests.cfgTests(_cfg)
            _tests.nodeCorrespondenceTest()
            _tests.edgeCorrespondenceTest()
            _tests.redundanceTest()

    data["necessaryBlocks"] = blockNum
    data["necessaryEdges"] = edgeNum

    for name, _cfg in tmpCFG_dict.items():
        tmpBranch, tmpMerge = countBranchMerge(_cfg)
        data["necessaryBranchingBlocks"] += tmpBranch
        data["necessaryMergingBlocks"] += tmpMerge
        data["necessaryBackEdges"] += countBackEdge(_cfg)
        
    # this part makes it one vertex per instruction
    oneInstGDict = dict()
    for name, _cfg in tmpCFG_dict.items():
        # this is the function that does the conversion (it's a constructor... but you know what i mean)
        currOIG = oneInstG_t(_cfg)
        oneInstGDict[name] = currOIG
        if Args.test:
            _tests = tests.oneInstGTests(_cfg, currOIG)
            _tests.instsCountTest()

    for name, currOIG in oneInstGDict.items():
        data["finalNodes"] += currOIG.countNodes()

    print("blocks: %d, branching %d, merging %d, necessary blocks: %d, necessary branching blocks: %d, necessary merging blocks: %d, edges: %d, back edges: %d, necessary edges: %d, necessary back edges: %d, insts: %d, semi relevant insts: %d, relevant insts: %d, funcs: %d, necessary funcs %d, final nodes %d"%(data["blocks"], data["branchingBlocks"], data["mergingBlocks"], data["necessaryBlocks"], data["necessaryBranchingBlocks"], data["necessaryMergingBlocks"], data["edges"], data["backEdges"], data["necessaryEdges"], data["necessaryBackEdges"], data["allInsts"], data["semiRelevant"], data["relevant"], data["funcs"], data["necessaryFuncs"], data["finalNodes"]))

    for name, currOIG in oneInstGDict.items():
        currOIG.outResult("outs/" + name + ".txt")
    
if __name__ == "__main__":
    graphReduction()


