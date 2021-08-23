import pdb

debug = False 
NOSY = False 
CHECK = True 
RECORD = False

def __dfs_visit(curr, vertices:dict) -> None:
    if curr.is_visited():
        return
    curr.visit()
    if not curr.has_insts():
        vertices[curr.get_name()] = curr

    for name, child in curr.get_children().items():
        __dfs_visit(child, vertices)
    return

def list_vertices(cfg) -> dict:
    rv = dict()
    root = cfg.get_root()
    cfg.clear_visit()
    __dfs_visit(root, rv)
    cfg.clear_visit()
    return rv

def create_bipartite_graph(curr, Vs: dict) -> None:
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

def delete_emptyNodes(emptyVertices: dict, cfg):
    Vs = cfg.get_vertices()
    for eName, eV in emptyVertices.items():
        create_bipartite_graph(eV, Vs)

def delete_redundantNodes(emptyVertices: dict, cfg):
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

def __count_nodes(curr):
    if curr.is_visited():
        return 0, 0
    curr.visit()
    vcount, ecount = 1, 0 
    for name, child in curr.get_children().items():
        ecount += 1
        tmp_vcount, tmp_ecount = __count_nodes(child)
        vcount += tmp_vcount; ecount += tmp_ecount
    return vcount, ecount 

def count_vertices(cfg):
    rv = __count_nodes(cfg.get_root())
    cfg.clear_visit()
    return rv

def printEV(empty_vertices):
    for empty_name, empty_v in empty_vertices.items():
        print(empty_name, end = ',')
        print(len(empty_v.get_parents()), end = ',')
        print(len(empty_v.get_children()), end = ':')
    print()

def further_simplify(cfg, allEV: bool):
    '''
    what to do
    1. list all the vertices that are empty
    2. create a bipartite graph for all of the edges that are empty
    '''
    empty_vertices = list_vertices(cfg)

    if allEV:
        delete_emptyNodes(empty_vertices, cfg)
    else:
        delete_redundantNodes(empty_vertices, cfg)
    
    vcount, ecount = count_vertices(cfg)
    
    return vcount, ecount

