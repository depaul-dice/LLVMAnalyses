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

def create_bipartite_graph(curr) -> None:
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

    # if there is no outgoing edges, you dont have to iterate through
    if len(dests) == 0:
        return

    # then for each src, add each dest as an oedge 
    # also for each dest, add each src as an iedge
    for name_src, src in srcs.items():
        for name_dest, dest in dests.items():
            src.append_oedge(dest)
            dest.append_iedge(src)

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

def traverse_check(name:str, curr) -> bool:
    if curr.is_visited():
        return True
    curr.visit()
    #print('now I am at %s'%(curr.get_name()))
    if curr.get_name() == name:
        return False
    for parent_name, parent in curr.get_parents().items():
        if parent_name == name:
            print('in curr name: %s, parent name: %s turned out to be the same'%(curr.get_name(), parent_name)) 
            return False
    for child_name, child in curr.get_children().items():
        if not traverse_check(name, child):
            return False
    return True

def check_integrity(name: str, cfg, target) -> bool:
    # checks if any of the vertex in the cfg has the name
    # if it does return false
    # else return true
    if target.get_type() == 'root':
        return True
        
    rv = traverse_check(name, cfg.get_root())
    cfg.clear_visit()

    return rv 

def further_simplify(cfg):
    '''
    what to do
    1. list all the vertices that are empty
    2. create a bipartite graph for all of the edges that are empty
    '''
    empty_vertices = list_vertices(cfg)
    # print("printing empty %d"%len(empty_vertices))
    flag = True
    currVertices = empty_vertices.copy()
    oldVertices = dict() 
    first = True
    cfg_name = cfg.get_name()
    
    while flag == True:
        flag = False
        if not first:
            currVertices = oldVertices.copy()
        first = False
        oldVertices.clear()
        assert len(oldVertices) == 0
        for name, eVertex in currVertices.items():
            if eVertex.get_type() == "root":
                continue
            srcs = eVertex.get_parents()
            dsts = eVertex.get_children()
            if name in srcs:  
                del srcs[name]
                assert name in dsts
                del dsts[name]
                flag = True
            
            if len(srcs) <= 1 and len(dsts) <= 1: 
                for src_name, src in srcs.items():
                    src.del_oedge(eVertex)
                for dst_name, dst in dsts.items():
                    dst.del_iedge(eVertex)

                for src_name, src in srcs.items():
                    for dst_name, dst in dsts.items():
                        src.append_oedge(dst)
                        dst.append_iedge(src)
                
                # create_bipartite_graph(eVertex)
                cfg.remove_vertex(name)
                flag = True
            else:
                oldVertices[name] = eVertex
        
    vcount, ecount = count_vertices(cfg)
    return vcount, ecount

