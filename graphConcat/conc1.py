import sys
import os
import os.path
from os import path
sys.setrecursionlimit(500000)
f = open("main.txt", "r")
affectedAddress = {}

class graph:
    def __init__(self,gdict=None):
        if gdict is None:
            gdict = []
        self.gdict = gdict

# Get the keys of the dictionary
    def getVertices(self):
        return list(self.gdict.keys())
    
    def edges(self):
        return self.findedges()

    def findedges(self):
        edgename = []
        for vrtx in self.gdict:
            for nxtvrtx in self.gdict[vrtx]:
                if {nxtvrtx, vrtx} not in edgename:
                    edgename.append({vrtx, nxtvrtx})
        return edgename

# Create the dictionary with graph elements

def getNodeElements(node):
	node = node.strip('\n').split(",")
	if node[1]=="epoint" or node[1]=="ret" or node[1] =="empty":

		return node[0],[node[1],[] if node[2] == '0' else node[5].split(":"), [] if node[3] == '0' else node[6].split(":"), [] if node[4] == '0' else node[7].split(":")]
	else:
		return node[0],[node[1],node[2],[] if node[3] == '0' else node[6].split(":"),[] if node[4] == '0' else node[7].split(":"),[] if node[5] == '0' else node[8].split(":")]

# Creating a graph

def createGraph(fileName):
	f = open(fileName + ".txt", "r")
	lines = f.readlines()
	graph_elements = {}
	for vertex in lines:
		(key,value) = getNodeElements(vertex)
		graph_elements[key] = value
	return graph_elements

def removeDuplicate(vertexCurr, prevVertices):
	vertArray = vertexCurr.split("_")
	filter_list = [k for k in prevVertices if vertArray[0] in k]
	if(len(filter_list) > 0 and ((len(vertArray) >= 2 and vertArray[1] == "copy") or len(vertArray) == 1 )):
		filter_list = [0 if len(k.split("_")) <= 2 else int(k.split("_")[2]) for k in filter_list if vertArray[0] + '_copy' in k]
		if len(filter_list) >= 1:
			val = max(filter_list) + 1
			if len(vertArray) == 1:
				# print(vertArray[0] + "_copy_" + str(val))
				result = vertArray[0] + "_copy_" + str(val)
			if len(vertArray) >= 2:
				# print(vertArray[0] + "_copy_" + str(val))
				result = vertArray[0] + "_copy_" + str(val)
		else:
			# print(vertArray[0] + "_copy")
			result = vertArray[0] + "_copy"
		
	elif(len(filter_list) > 0 and len(vertArray) >= 2 and vertArray[1] != "copy" and "copy" in vertexCurr):
		filter_list = [0 if len(k.split("_")) <= 3 else int(k.split("_")[3]) for k in filter_list if vertArray[0] + "_" + vertArray[1] + '_copy' in k]
		val = max(filter_list) + 1
		if len(vertArray) >= 3:
			# print(vertArray[0] + "_" + vertArray[1] + "_copy_" + str(val))
			result = vertArray[0] + "_" + vertArray[1] + "_copy_" + str(val)

	elif len(filter_list) == 0:
		result = vertexCurr

	else:
		filter_list = [0 if len(k.split("_")) <= 3 else int(k.split("_")[3]) for k in filter_list if vertexCurr + '_copy' in k]
		if len(filter_list) >= 1:
			val = max(filter_list) + 1
			if len(vertArray) == 1:
				# print(vertArray[0] + "_" + vertArray[1] + "_copy_" + str(val))
				result = vertArray[0] + "_" + vertArray[1] + "_copy_" + str(val)
			if len(vertArray) >= 2:
				# print(vertArray[0] + "_" + vertArray[1] + "_copy_" + str(val))
				result = vertArray[0] + "_" + vertArray[1] + "_copy_" + str(val)
		else:
			# print(vertArray[0] + "_copy")
			result = vertexCurr + "_copy"

	flag = 0 if result == vertexCurr else 1

	return result,flag,vertexCurr


def concatenateGraph(affAdd, PGvertex, fileName, outgoingEdges, incomingEdges, backEdges, prevVertices):
	nextGraph = createGraph(fileName)
	temp = {}
	count = 0
	prevVertex = ""
	ndPrevVertex = ""
	head = 0
	# print(vertex)
	count = 0
	for vertex in nextGraph:
		
		vertexCurr,flag,originalVertex = removeDuplicate(vertex, prevVertices)
		
		if head == 0:
			affectedAddress[affAdd] = vertexCurr
			head = head + 1

		val = nextGraph[vertex]
		if prevVertex != "" and flag > 0:
			count = count + 1
			newEdges = [k for k in temp[prevVertex] if isinstance(k,list)]
			
			if count == 1:
				prevVal1 = newEdges[1]
				prevVal2 = newEdges[2]
			elif count > 1:
				prevVal1 = [ndPrevVertex]
				prevVal2 = newEdges[2]

			prevValues = [k for k in temp[prevVertex] if not isinstance(k,list)]
			
			newEdges = [vertexCurr if k == originalVertex else k for k in newEdges[0]]
			
			prevValues.append(newEdges)
			prevValues.append(prevVal1)
			prevValues.append(prevVal2)
			
			temp.update({prevVertex:prevValues})
		if val[0] == 'ret':
			set1 = set(nextGraph[vertex][2])
			set2 = set([prevVertex])
			res = set2 - set1
			set1 = list(set1) + list(res)

			if count > 1:
				set1 = [prevVertex]

			temp[vertexCurr]=[val[0],outgoingEdges,set1,backEdges]

		elif val[0] == 'epoint':
			# print([PGvertex])
			temp[vertexCurr]=[val[0],nextGraph[vertex][1],[PGvertex],nextGraph[vertex][3]]

		else:
			temp[vertexCurr]=nextGraph[vertex]
		
		ndPrevVertex = prevVertex
		prevVertex = vertexCurr
		prevVer2 = vertex
		
	return temp


def replacePrevVertexEdges(concGraph, prevVal, currNode):
	head = ''
	for vertex in concGraph:
		head = vertex
		break
	temp = []
	for val in prevVal:
		if val == currNode:
			temp.append(head)
		else:
			temp.append(val)

	return temp



def fileCrawl(graphOut,prevVertex):
	functionDetected = 0
	temp = {}
	# prevVertex = ""

	count = 0
	for vertex in graphOut:

		val = graphOut[vertex]
		if val[0] == 'funccall' and functionDetected == 0:
			g = graph(temp)
			concGrp = concatenateGraph(vertex,prevVertex,val[1],val[2],val[3],val[4],g.getVertices())
			
			# print("if \n")
			# print(concGrp)
			# print("end if \n")

			temp.update(concGrp)
			
			functionDetected = 1
			prevVal = graphOut[prevVertex]
			currentVal = graphOut[vertex]
					
			if prevVal[0] == 'epoint' or prevVal[0]=='ret' or prevVal[0] == 'empty':
				updtVal = [prevVal[0],replacePrevVertexEdges(concGrp,prevVal[1],vertex)]
				updtVal.append(prevVal[2])
				updtVal.append(prevVal[3])
				temp.update({prevVertex:updtVal})
				# currentVal.remove(currentVal[2])
				# currentVal.insert(2,[prevVertex])

				# temp.update({vertex:currentVal})

		else:
			temp[vertex]=graphOut[vertex]
		
		prevVertex = vertex

	# print(temp)
	# print('\n')
	if functionDetected == 1:
			fileCrawl(temp,prevVertex)
	else:
		result = temp
		# print(affectedAddress)
		result = eleminateChangedAddress(affectedAddress, result)
		writeOutput(result)

def eleminateChangedAddress(affectedAddress, result):
	g = graph(affectedAddress)
	Vertices = g.getVertices()
	# print(Vertices)
	# print(affectedAddress['0x970220_2'])
	
	for vertex in result:
		val = result[vertex]
		# print(val)

		if val[0] == 'epoint' or val[0] == 'empty' or val[0] == 'ret':
			dstEdge = val[1]
			srcEdge = val[2]
			backEdge = val[3]
			dstEdgeFin = []
			srcEdgeFin = []
			backEdgeFin = []
			if dstEdge:
				for dst in dstEdge:
					if dst in Vertices:
						dstEdgeFin.append(affectedAddress[dst])
					else:
						dstEdgeFin.append(dst)
			if srcEdge:
				for src in srcEdge:
					if src in Vertices:
						srcEdgeFin.append(affectedAddress[src])
					else:
						srcEdgeFin.append(src)
			if backEdge:
				for backed in backEdge:
					if backed in Vertices:
						backEdgeFin.append(affectedAddress[backed])
					else:
						backEdgeFin.append(backed)

			updtVal = [val[0], dstEdgeFin, srcEdgeFin, backEdgeFin]
			

		else:
			dstEdge = val[2]
			srcEdge = val[3]
			backEdge = val[4]
			dstEdgeFin = []
			srcEdgeFin = []
			backEdgeFin = []
			if dstEdge:
				for dst in dstEdge:
					if dst in Vertices:
						dstEdgeFin.append(affectedAddress[dst])
					else:
						dstEdgeFin.append(dst)

			for src in srcEdge:
				if src in Vertices:
					srcEdgeFin.append(affectedAddress[src])
				else:
					srcEdgeFin.append(src)
			for backed in backEdge:
				if backed in Vertices:
					backEdgeFin.append(affectedAddress[backed])
				else:
					backEdgeFin.append(backed)
			updtVal = [val[0], val[1], dstEdgeFin, srcEdgeFin, backEdgeFin]

		result.update({vertex:updtVal})
		
	return result


def writeOutput(result):
	if(path.exists("result.txt")):
		os.remove("result.txt")
	original_stdout = sys.stdout
	for adjList in result:
		val = result[adjList]

		# print(val)
		typeCall = val[0]
		if typeCall == 'epoint' or typeCall == 'ret' or typeCall == 'empty':

			if not result[adjList][1]:
				dstEdge = 'na'
				leng1 = 0
			else:
				leng1 = len(result[adjList][1])
				dstEdge = ':'.join(result[adjList][1])
				
			if not result[adjList][2]:
				srcEdge = 'na'
				leng2 = 0
			else:
				srcEdge = ':'.join(result[adjList][2])
				leng2 = len(result[adjList][2])
				
			if not result[adjList][3]:
				backEdge = 'na'
				leng3 = 0
			else:
				backEdge = ':'.join(result[adjList][3])
				leng3 = len(result[adjList][3])
				
			with open('result.txt', 'a+') as f:

			    sys.stdout = f # Change the standard output to the file we created.
			    print(adjList+','+ result[adjList][0]+ ',' + str(leng1) + ',' + str(leng2) + ',' + str(leng3) + ',' + dstEdge + ',' + srcEdge + ',' + backEdge )
			    sys.stdout = original_stdout # Reset the standard output to its original value
		else:
			if not result[adjList][2]:
				dstEdge = 'na'
				leng1 = 0
			else:
				leng1 = len(result[adjList][2])
				dstEdge = ':'.join(result[adjList][2])
				
			if not result[adjList][3]:
				srcEdge = 'na'
				leng2 = 0
			else:
				srcEdge = ':'.join(result[adjList][3])
				leng2 = len(result[adjList][3])
				
			if not result[adjList][4]:
				backEdge = 'na'
				leng3 = 0
			else:
				backEdge = ':'.join(result[adjList][4])
				leng3 = len(result[adjList][4])

			with open('result.txt', 'a+') as f:
			    sys.stdout = f # Change the standard output to the file we created.
			    print(adjList+','+ result[adjList][0]+ ',' + str(result[adjList][1]) + ',' + str(leng1) + ',' + str(leng2) + ',' + str(leng3) + ',' + dstEdge + ',' + srcEdge + ',' + backEdge)
			    sys.stdout = original_stdout # Reset the standard output to its original value

	print('\n')
	

	exit()

def main(mainGraph):
	fileCrawl(mainGraph,'')
	print(result)

mainGraph = createGraph("main")
main(mainGraph)


