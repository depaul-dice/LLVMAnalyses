import re
import os
import sys

import parseDot
import CONSTANTS as C

class CFGParser:
    funcNamePattern2Rename = r"[\w\_]+\.(\d+)"
    cfgNamePattern = r'\"CFG\ for\ \'([\w\.]+)\'\ function\"'
    bitcast_pattern = r'(%\d+)\s=\sbitcast\s.*%struct\._IO_FILE\.\d+.*\s@(\w*)\sto\s(.+)'
    ret_pattern = r'^ret\s'
    func_pattern = r'\s*call\s+' # changed this to + from *
    fname_pattern = r'@([A-Za-z0-9_][\w_]*([.?]\w*|))\('
    bitcastResolve_pattern = r'%\d+\s=\s(tail\s|)call\s(%struct._IO_FILE|)(i\d+|)\*?\s(%\d+)\('

    def __init__(self, cfg_dict: dict, notFound_dict: dict, Args):
        self.cfg_dict = cfg_dict 
        self.notFound_dict = notFound_dict
        self.Args = Args

    def find_syscalls(self, inst: str) -> (list, int):
        if inst.find('syscall') == -1:
            return None
        for pattern in C.syscall_patterns:
            p = re.compile(pattern)
            m = re.findall(p, inst)
            if len(m) > 0:
                if len(m) >= 2:
                    raise Exception("syscall found twice in the instruction")
                return ['syscall'], int(m[0])
        if inst.find('__syscall_ret') == -1:
            raise Exception(inst + ': this could not be parsed')
        return None

    # this is the messiest function of all time
    def inst2keep(self, inst: str, bitcasts: dict) -> (list, int):
        m = re.findall(self.ret_pattern, inst)
        if len(m) > 0:
            return ['ret'], -1
        m = re.search(self.bitcast_pattern, inst)
        if m:
            # print(m.group(1) + ':' + m.group(2) + ':' + m.group(3))
            if m.group(1) in bitcasts:
                raise Exception(m.group(1) + " already in bitcasts, " + m.group(2) + " vs. " + bitcasts[m.group(1)])
            bitcasts[m.group(1)] = m.group(2)

            return None

        m = re.findall(self.func_pattern, inst)
        rv = list() 
        flag = False
        if len(m) > 0:
            syscalls = self.find_syscalls(inst)
            if syscalls != None:
                return syscalls 
            p = re.compile(self.fname_pattern)
            matches = p.finditer(inst)
            for match in matches:
                funcname = inst[match.start() + 1:match.end() - 1]
                if funcname.find('llvm.') != -1 or funcname.find('__syscall_ret') != -1 or funcname.find('__vm_wait') != -1 or funcname.find('expand_heap.') != -1 or funcname.find('__PRETTY_FUNCTION__.') != -1 or funcname in C.unnec:
                    flag = True
                    continue
                if funcname.find('__syscall_cp') != -1:
                    print(inst)
                    raise Exception('__syscall_cp not caught')
                rv.append(funcname)
            if len(rv) == 0 and flag == False:
                # see if it's resolvable

                n = re.search(self.bitcastResolve_pattern, inst)
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

    def not_line(self, inst: str) -> bool:
        pattern = re.compile(r'^\.\.\.')
        matches = pattern.finditer(inst)
        rv = sum(1 for _ in matches)
        if rv > 0:
            return True
        elif rv == 0:
            return False
        else:
            raise Exception('no negative values allowed')

    def parse_block(self, block, directory: str, bitcasts: dict, infos: dict) -> None:
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
            if len(old_insts) > 0 and self.not_line(old_insts[0]):
                old_insts[0] = old_insts[0][4:]
                concat_flag = True
                continue
            # print('new inst: ' + inst)
            parsed = self.inst2keep(inst, bitcasts)
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
                            if func in C.func_dict:
                                tmpfunc = C.func_dict[func]
                                filename = tmpfunc + '.dot'
                                # print('translating: ' + filename)
                            elif False:
                                pass # you need to add the case where \w+\d+ here
                            else:
                                if func not in self.notFound_dict:
                                    print("%s not found"%func)
                                    self.notFound_dict[func] = 1
                                    func_flag = True
                                continue
                                # raise Exception('file not found: %s'%filename)

                        if self.Args.recursiveParse: # I think this needs to be changed
                            self.parse_cfg(directory, filename, infos)
                    new_insts.append((func, num)) 
        block.set_insts(new_insts)
        infos["semiRelevant"] += len(new_insts)
        return

    def checkIfFileExists(funcName: str) -> str:
        if funcName in C.func_dict:
            tmpfunc = C.func_dict[funcName]
            filename = tmpfunc + '.dot'
            return filename

        if funcName not in self.notFound_dict:
            print("%s not found"%func)
            self.notFound_dict[func] = 1
        return None

    def parse_func_topdown(self, cfg_, directory: str, infos: dict) -> None:
        vertices = cfg_.get_vertices()
        bitcasts = dict()
        for vName, vertex in vertices.items():
            self.parse_block(vertex, directory, bitcasts, infos)
        if len(bitcasts) != 0:
            # print(bitcasts, file = sys.stderr)
            # raise Exception(cfg_.name)
            pass # this is just a filler, the function is actually complete
     
    def parse_cfg(self, directory: str, filename: str, infos: dict):
        path = os.path.join(directory, filename) 
        if not os.path.exists(path):
            raise Exception(path + " does not exist, exitting...")
        
        _cfg, flag = parseDot.parse_dot(path, self.cfg_dict, infos)
        if flag:
            return _cfg
        
        self.parse_func_topdown(_cfg, directory, infos)
        
        # I want to count the number of vertices and edges here (before simplification)
        
        if _cfg.name in self.cfg_dict and self.cfg_dict[_cfg.name] != None:
            raise Exception('this should be new cfg')
        elif not _cfg.name in self.cfg_dict:
            raise Exception(_cfg.name + ' should be in the dict')
        else:
            self.cfg_dict[_cfg.name] = _cfg
        infos["funcs"] += 1
        return _cfg

    def parseCFGName(self, name: str) -> str:
        # pattern = r'\"CFG\ for\ \'([\w\.]+)\'\ function\"'
        p = re.compile(self.cfgNamePattern)
        m = re.match(p, name)
        if m == None:
            print(name)
            sys.exit(1)
        return m.group(1) 


if __name__ == "__main__":
    Inst = InstParser() 
