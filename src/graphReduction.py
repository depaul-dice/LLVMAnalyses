import parseDot 
import tools 
from simplify import further_simplify
from oneInstG import oneInstG_t
import tests
import sys
import re
import os
import shutil
from config import args
from removeSysFuncs import RemoveSysFuncs
import parseCFG

Args = args() 
cfg_dict = dict()
notFound_dict = dict()

func_dict = {
       '__libc_exit_fini' :'libc_exit_fini',
        'fdopen': '__fdopen',
        '___errno_location': '__errno_location',
        'ofl_lock': '__ofl_lock',
        '__isoc99_sscanf': 'sscanf',
        # '__lctrans_impl': '__lctrans', this was so wrong, they were two different funcs, happened when looking at chown
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
 
def removeSysfuncs(data: dict, _file: str, tmpCFG_dict: dict, func_dict: dict):
    # don't worry about these for now
    syscall_dict = dict()
    # this function just finds whether the function includes the syscall or not
    find_syscall(tmpCFG_dict[_file], syscall_dict, tmpCFG_dict, func_dict)
    # below is the sys file
    writeSyscallDict(syscall_dict, "syscall.txt")

    for funcName, necessary in syscall_dict.items():
        if necessary:
            data["necessaryFuncs"] += 1

    # this function finds which function has what
    specSyscallDict = dict()
    find_specSyscall(tmpCFG_dict[_file], specSyscallDict, tmpCFG_dict, func_dict)
    
    for funcName, necessary in syscall_dict.items():
        if not necessary:
           del tmpCFG_dict[funcName] 

    unnec_insts = 0
    for name, _cfg in tmpCFG_dict.items():
        unnec_insts += deleteUnnecessaryFuncs(_cfg, syscall_dict, func_dict)
    data["relevant"] = data["semiRelevant"] - unnec_insts

def writeTmp(src: str):
    dst = ".tmp"
    try: os.mkdir(dst)
    except FileExistsError:
        print(dst + ' already exists')
    for filename in os.listdir(src):
        with open(os.path.join(src, filename), 'r') as file:
            lines = file.read()
            lines = lines.replace('\\\"', '')
            with open(os.path.join(dst, filename), 'w') as g:
                g.write(lines)

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
    writeTmp(Args.directory)
    directory = '.tmp'
    # directory = Args.directory 
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
    pcfg = parseCFG.CFGParser(cfg_dict, notFound_dict, unnec, func_dict, Args, syscall_patterns)
    _cfg = pcfg.parse_cfg(directory, filename, data)
    
    old_names = list()
    tmpCFG_dict = dict()
    for name, _cfg in cfg_dict.items():
        old_names.append(name)
        name = pcfg.parseCFGName(name) 
        # go through cfg and find if there's a syscall in them
        tmpCFG_dict[name] = _cfg
        _cfg.name = name

    for name, _cfg in cfg_dict.items():
        tmpBranch, tmpMerge = countBranchMerge(_cfg)
        data["branchingBlocks"] += tmpBranch
        data["mergingBlocks"] += tmpMerge
        data["backEdges"] += countBackEdge(_cfg)

    if Args.removeSysfuncs:
        rsf = RemoveSysFuncs() # I can probably the argument later
        rsf.removeSysFuncs(data, _file, tmpCFG_dict, func_dict)
       
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


