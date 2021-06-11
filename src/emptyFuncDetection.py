
from oneInstG import typeNode, oneInstG_t
import sys
deleteFunc = {
        '__stdout_FILE': 1, 
        '__stderr_FILE': 1, 
        }

convertFunc = {
        '__lctrans_impl': '__lctrans',
        'ofl_lock': '__ofl_lock',
        '__isoc99_sscanf': 'sscanf',
        '__PRETTY_FUNCTION__.read_min': 'read_min',
        '__PRETTY_FUNCTION__.resize_prob': 'resize_prob',
        '__libc_exit_fini': 'libc_exit_fini',
        '___errno_location': '__errno_location',
        'fdopen': '__fdopen',
        }

def findEmptyRecurse(funcname, graphs, parsedGs) -> bool:
    if funcname in parsedGs:
        return parsedGs[funcname] 

    try:
        G = graphs[funcname]
    except KeyError as e:
        if '___' in funcname:
            funcname = funcname.replace('___', '__')
            G = graphs[funcname]
        elif funcname in deleteFunc:
            return False
        elif funcname in convertFunc:
            funcname = convertFunc[funcname]
            G = graphs[funcname]
        else:
            raise Exception("this error is still not handled")
    queue = list()
    queue.append(G.getep())
    parsedGs[funcname] = -1
    sysFound = False

    while len(queue) > 0:
        currV = queue.pop(0)
        if currV.color == 1:
            continue

        if currV.typeNode == typeNode.SYSCALL:
            sysFound = True 

        elif currV.typeNode == typeNode.FUNCCALL:
            if findEmptyRecurse(currV.funcname, graphs, parsedGs):
                sysFound = True

        currV.color = 1
        for name, oEdge in currV.get_oEdges().items():
            queue.append(oEdge)
    
    if sysFound:
        parsedGs[funcname] = 1
        return True 
    else:
        parsedGs[funcname] = 0
        return False 
    

def findEmptyFunc(graphs):

    mainG = graphs["main"] 
    queue = list() 
    queue.append(mainG.getep())
    parsedGs = dict()
    parsedGs["main"] = -1 
    sysFound = False

      
    while len(queue) > 0:
        currV = queue.pop(0)
        # if currV is visited alr, we skip
        if currV.color == 1:
            continue

        if currV.typeNode == typeNode.SYSCALL:
        # if currV has syscalls, just mark the thing as one, and return 1 too.
            sysFound = True
            
        elif currV.typeNode == typeNode.FUNCCALL:
        # if currV has a function call, we go in and check if the function has a system call
        # make sure to take care of the recursive case
            if currV.funcname in convertFunc:
                currV.funcname = convertFunc[currV.funcname]
            if findEmptyRecurse(currV.funcname, graphs, parsedGs):
                sysFound = True

        #just shove the outgoing edges 
        currV.color = 1
        for name, oEdge in currV.get_oEdges().items():
            queue.append(oEdge)

    if sysFound:
        parsedGs["main"] = 1
    else:
        parsedGs["main"] = 0
    
    return parsedGs

def deleteEmptyNode(currNode):
    iEdges = currNode.get_iEdges()
    oEdges = currNode.get_oEdges()
    for iEdgeName, iEdge in iEdges.items():
        if iEdge == currNode:
            continue
        for oEdgeName, oEdge in oEdges.items():
            if oEdge == currNode:
                continue
            iEdge.append_oEdge(oEdgeName, oEdge)
            oEdge.append_iEdge(iEdgeName, iEdge)
            oEdge.delete_iEdge(currNode.id)
        iEdge.delete_oEdge(currNode.id)

def clearTraversal(cfg):
    tmpDict = dict()
    ep = cfg.getep()
    queue = list()
    queue.append(ep)
    while len(queue) > 0:
        curr = queue.pop(0)
        if curr.id in tmpDict:
            continue
        curr.color = 0
        tmpDict[curr.id] = 1
        for name, oEdge in curr.get_oEdges().items():
            queue.append(oEdge)

def removeEmptyNodes(cfg, emptyNodes: dict):
    flag = True 
    currNodes = emptyNodes.copy()
    while flag:
        flag = False
        oldNodes = currNodes.copy() 
        currNodes = dict()
        for name, node in oldNodes.items():
            srcs = node.get_iEdges()
            dsts = node.get_oEdges()
            bdsts = node.get_bEdges()
            # bsrcs = node.get_iBEdges()

            # if node has a self-loop remove it
            if name in srcs:
                del srcs[name] 
                assert name in bdsts
                del bdsts[name]

            # if node has only one or zero iEdge and one or zero oEdge, remove it
            if len(srcs) <= 1 and len(dsts) + len(bdsts) <= 1:
                for src_name, src in srcs.items():
                    src.delete_oEdge(name)
                    for dst_name, dst in dsts.items():
                        dst.delete_iEdge(name)
                        src.append_oEdge(dst_name, dst)
                        dst.append_iEdge(src_name, src)
                    
                    for bdst_name, bdst in bdsts.items():
                        bdst.delete_iEdge(name)
                        # bdst.delete_iBEdge(name)
                        src.append_bEdge(bdst_name, bdst)
                        bdst.append_iEdge(src_name, src)
                        # bdst.append_iBEdge(src_name, src)

                cfg.deleteNode(name)
                flag = True
            else:
                assert name not in currNodes
                currNodes[name] = node

def traverseDeleteEmptyFunccall(cfg, emptyFuncDict):
    queue = list()
    queue.append(cfg.getep())
    clearTraversal(cfg)
    emptyNodes = dict()
    while len(queue) > 0:
        curr = queue.pop(0)
        if curr.color == 1:
            continue
        curr.color = 1 
        if curr.typeNode == typeNode.FUNCCALL and curr.funcname in convertFunc:
            curr.funcname = convertFunc[curr.funcname]

        '''
        if curr.typeNode == typeNode.FUNCCALL and emptyFuncDict[curr.funcname] == 0:
            curr.typeNode = typeNode.EMPTY
            curr.funcname = None
        '''

        if curr.typeNode == typeNode.EMPTY:
            # you need to delete this node here
            emptyNodes[curr.id] = curr
            '''
            deleteEmptyNode(curr)
            cfg.deleteNode(curr.id)
            '''

        oEdges = curr.get_oEdges()
        for _id, node in oEdges.items():
            queue.append(node)
    removeEmptyNodes(cfg, emptyNodes)

def deleteEmptyFuncCall(oneInstGDict, emptyFuncDict):
    # first deleting all the unnecessary functions 
    for name, num in emptyFuncDict.items():
        if num == 0:
            del oneInstGDict[name]

    # second deleting all the unnecessary funcCall nodes 
    for name, cfg in oneInstGDict.items():
        traverseDeleteEmptyFunccall(cfg, emptyFuncDict)

    return oneInstGDict
