'''
Copyright (c) 2021 Yuta Nakamura. All rights reserved.
'''
from enum import Enum
import parseDot
import sys

# this is a control flow graph with only one instruction per node in it
# I will parse the normal graph to get one
# it takes in the original graph when taking in, and outputs result when method is called

class typeNode(Enum):
    EPOINT = 1;
    SYSCALL = 2;
    FUNCCALL = 3;
    RET = 4;
    EMPTY = 5;
    NULL = 6;

class oneInstG_t:
    # constructor
    def __init__(self, graph):
        iEdgeSupply = dict()
        iEdgeDemand = dict()
        oEdgeDemand = dict() # (vertex in demand in str, client vertices)
        self.name = graph.name
        ePoint = graph.get_root()
        self.__nodes = dict()
        self.__parseEntryPoint(ePoint, oEdgeDemand, iEdgeSupply)
        vertices = graph.get_vertices() 
         
        for vName, vertex in vertices.items():
            # if it is an entryPoint skip
            if vertex.get_type() == "root":
                continue
            self.__parseVertex(vName, vertex, oEdgeDemand, iEdgeSupply, iEdgeDemand) 
        
        for demand, clients in oEdgeDemand.items():
            demandV = self.__nodes[demand]
            if demandV == None:
                raise Exception("vertex for oedge not found")
            assert type(clients) == list
            for client in clients:
                client.append_oEdge(demand, demandV)

        for client, demands in iEdgeDemand.items():
            # client: Node, demands: list[str]
            for demand in demands:
                supply = iEdgeSupply[demand]
                if supply == None:
                    raise Exception("vertex for iEdge not found")
                client.append_iEdge(supply.id, supply)
        self.__findBackEdges()

    def __findBackEdges(self) -> None:
        # clearing the traversal of before
        for name, node in self.__nodes.items():
            node.color = 0
        history = dict()
        history[self.__entryPoint.id] = self.__entryPoint 
        self.__findBackEdgeRecursive(history, self.__entryPoint)
        for name, node in self.__nodes.items():
            node.color = 0

    def __findBackEdgeRecursive(self, history: dict, curr):
        if curr.color == 1:
            return
        curr.color = 1 
        outDelete = list()
        #inDelete = dict()
        for name, oEdge in curr.get_oEdges().items():
            if name in history:
                # back edge is found
                outDelete.append(name)
                curr.append_bEdge(name, oEdge)
                oEdge.append_iEdge(curr.id, curr)
            else:
                histCopy = history.copy()
                histCopy[name] = oEdge
                self.__findBackEdgeRecursive(histCopy, oEdge)

        for name in outDelete:
            curr.delete_oEdge(name)
        '''
        for __id, oEdge in inDelete.items():
            oEdge.delete_iEdge(__id)
        '''
           
    def __parseEntryPoint(self, ePoint, oEdgeDemand: dict, iEdgeSupply: dict) -> None:
        insts = ePoint.get_insts()
        oedges = ePoint.get_children()
        iedges = ePoint.get_parents()
        assert len(iedges) == 0
        prevNode = None

        if len(insts) == 0:
            # make this as an entryPoint
            currNode = oneInstV(ePoint.get_name(), "__entryPoint", len(oedges), -1) 
            for edgeName, dst in oedges.items():
                if edgeName not in oEdgeDemand:
                    oEdgeDemand[edgeName] = list()
                oEdgeDemand[edgeName].append(currNode)
            self.__nodes[ePoint.get_name()] = currNode
            self.__entryPoint = currNode
            iEdgeSupply[ePoint.get_name()] = currNode

        elif len(insts) > 0:
            baseName = ePoint.get_name() 
            prevNode = oneInstV(baseName, "__entryPoint", 1, -1)
            self.__entryPoint = prevNode
            i = 0
            while i < len(insts) - 1:
                currNode = oneInstV(baseName + "_" + str(i), insts[i][0], 1, insts[i][1])
                assert prevNode != None        
                prevNode.append_oEdge(currNode.id, currNode)
                currNode.append_iEdge(prevNode.id, prevNode)
                self.__nodes[prevNode.id] = prevNode
                prevNode = currNode
                i += 1
            # last node is special
            currNode = oneInstV(baseName + "_" + str(i), insts[i][0], len(oedges), insts[i][1]) 
            assert prevNode != None
            prevNode.append_oEdge(currNode.id, currNode)
            currNode.append_iEdge(prevNode.id, prevNode)
            self.__nodes[prevNode.id] = prevNode
            for edgeName, dst in oedges.items():
                if edgeName not in oEdgeDemand:
                    oEdgeDemand[edgeName] = list()
                oEdgeDemand[edgeName].append(currNode)
            self.__nodes[currNode.id] = currNode 
            iEdgeSupply[ePoint.get_name()] = currNode
            
        else:
            raise Exception("negative number of insts")

    def __parseVertex(self, vName:str, vertex, oEdgeDemand: dict, iEdgeSupply: dict, iEdgeDemand: dict) -> None:
        # how many instructions does it have?
        # is it more than 0?
        # is it multiple
        insts = vertex.get_insts()
        oedges = vertex.get_children() 
        iedges = vertex.get_parents()
        
        if len(insts) == 1:
            # create vertex first
            currNode = oneInstV(vertex.get_name(), insts[0][0], len(oedges), insts[0][1])  
            iEdgeDemand[currNode] = list()
            for iEdgeName in iedges:
                iEdgeDemand[currNode].append(iEdgeName)

            for edgeName, dst in oedges.items():
                if edgeName not in oEdgeDemand:
                    oEdgeDemand[edgeName] = list()
                oEdgeDemand[edgeName].append(currNode)
            self.__nodes[currNode.id] = currNode
            iEdgeSupply[currNode.id] = currNode

        elif len(insts) == 0:
            currNode = oneInstV(vertex.get_name(), None, len(oedges))
            iEdgeDemand[currNode] = list()
            for iEdgeName in iedges:
                iEdgeDemand[currNode].append(iEdgeName)

            for edgeName, dst in oedges. items():
                if edgeName not in oEdgeDemand:
                    oEdgeDemand[edgeName] = list()
                oEdgeDemand[edgeName].append(currNode)

            self.__nodes[currNode.id] = currNode
            iEdgeSupply[currNode.id] = currNode

        else:
            prevNode = None
            i = 0
            # for i in range(len(insts) - 1):
            while i < len(insts) - 1:
                if i == 0:
                    currNode = oneInstV(vertex.get_name(), insts[i][0], 1, insts[i][1])
                    iEdgeDemand[currNode] = list()
                    for iEdgeName in iedges:
                        iEdgeDemand[currNode].append(iEdgeName)

                else:
                    currNode = oneInstV(vertex.get_name() + "_" + str(i), insts[i][0], 1, insts[i][1])
                if prevNode != None:
                    prevNode.append_oEdge(currNode.id, currNode)
                    currNode.append_iEdge(prevNode.id, prevNode)
                    self.__nodes[prevNode.id] = prevNode
                prevNode = currNode
                i += 1

            # last node needs a special care
            try:
                currNode = oneInstV(vertex.get_name() + "_" + str(i), insts[i][0], len(oedges), insts[i][1])
            except:
                print(vertex.get_name())
                print(insts)
                print(i)
                sys.exit(1)

            assert prevNode != None
            prevNode.append_oEdge(currNode.id, currNode)
            currNode.append_iEdge(prevNode.id, prevNode)
            self.__nodes[prevNode.id] = prevNode
            
            for edgeName, dst in oedges.items():
                if edgeName not in oEdgeDemand:
                    oEdgeDemand[edgeName] = list()
                oEdgeDemand[edgeName].append(currNode)
            self.__nodes[currNode.id] = currNode
            iEdgeSupply[vertex.get_name()] = currNode
        
    # method
    def outResult(self, filename) -> None:
        with open(filename, 'w') as f:
            for vName, vertex in self.__nodes.items():
                vertex.outResult(f)
    def outResult2(self, f) -> None:
        for vName, vertex in self.__nodes.items(): 
            vertex.outResult2(f)

    def getep(self):
        return self.__entryPoint

    def deleteNode(self, _id):
        del self.__nodes[_id]
    
    def countNodes(self) -> int:
        return len(self.__nodes)


    # member
    # __entryPoint = None;
    # __numNodes = -1;
    # __nodes

class oneInstV:
    def __init__(self, __id: str, __type: str, numOutEdges: int, sysNum = -1) -> None:
        self.id = __id
        self.typeNode = self.__convertType(__type)
        self.__sysNum = sysNum
        self.__outEdges = dict() 
        self.__inEdges = dict()
        self.__backEdges = dict()
        self.color = 0

    def __convertType(self, __type:str) -> typeNode:
        if __type == "__entryPoint":
            return typeNode.EPOINT
        elif __type == "syscall":
            return typeNode.SYSCALL
        elif __type == "ret":
            return typeNode.RET
        elif __type == None:
            return typeNode.EMPTY
        else: 
            self.funcname = __type
            return typeNode.FUNCCALL

    def get_bEdges(self) -> dict:
        return self.__backEdges

    def append_bEdge(self, __id: str,  __bEdge)-> None:
        if __id in self.__backEdges and __bEdge != self.__backEdges[__id]:
            raise Exception("bEdge not matching")
        self.__backEdges[__id] = __bEdge

    def get_oEdges(self) -> dict:
        return self.__outEdges

    def append_oEdge(self, __id: str, __oEdge) -> None:
        if __id in self.__outEdges:
            if __oEdge != self.__outEdges[__id]:
                raise Exception("oEdge not matching")
        self.__outEdges[__id] = __oEdge

    def delete_oEdge(self, __id: str) -> None:
        if not __id in self.__outEdges:
            return
        del self.__outEdges[__id]
    
    def get_iEdges(self) -> dict:
        return self.__inEdges

    def append_iEdge(self, __id: str, __iEdge) -> None:
        if __id in self.__inEdges:
            if __iEdge != self.__inEdges[__id]:
                raise Exception("iEdge not matching")
        self.__inEdges[__id] = __iEdge

    def delete_iEdge(self, __id: str) -> None:
        if not __id in self.__inEdges:
            return 
        del self.__inEdges[__id]

    def outResult(self, f):
        f.write(self.id + ',')
        if self.typeNode == typeNode.EPOINT:
            f.write('epoint,')
        elif self.typeNode == typeNode.SYSCALL:
            f.write('syscall,')
            f.write(str(self.__sysNum) + ',')
        elif self.typeNode == typeNode.FUNCCALL:
            f.write('funccall,')
            f.write(self.funcname + ',')
        elif self.typeNode == typeNode.EMPTY:
            f.write('empty,')
        else:
            f.write('ret,')

        f.write(str(len(self.__outEdges)) + ',')
        f.write(str(len(self.__inEdges)) + ',')
        f.write(str(len(self.__backEdges)) + ',')
        newbie = True 
        if len(self.__outEdges) == 0:
            f.write('na')
        for edgeName in self.__outEdges:
            if newbie:
                newbie = False
            else:
                f.write(':')
            f.write(edgeName)
        f.write(',')

        newbie = True
        if len(self.__inEdges) == 0:
            f.write('na')
        for edgeName in self.__inEdges:
            if newbie:
                newbie = False
            else:
                f.write(':')
            f.write(edgeName)
        f.write(',')

        newbie = True
        if len(self.__backEdges) == 0:
            f.write('na')
        for edgeName in self.__backEdges:
            if newbie:
                newbie = False
            else:
                f.write(':')
            f.write(edgeName)

        f.write('\n')
        
    # member
    # __typenode = typenode.null;  
    # __numoutedges = -1;
    # __sysnum = -1
    # __outEdges = None 
    # color = 0 
