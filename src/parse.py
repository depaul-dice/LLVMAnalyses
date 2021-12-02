import re

class InstParser:
    def __init__(self):
        pass
    def inst2keep(self, inst: str, bitcasts: dict) -> (list, int):
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

if __name__ == "__main__":
    Inst = InstParser() 
