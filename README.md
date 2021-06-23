# SIMPLIFIER #

This is a program that takes in a set of dotfiles that are created with the llvm bitcode.
The program's objective is to simplify the graphs that would only have instructions that are relevant to system calls. System calls are chosen because [Sciunit](sciunit.run) keeps track of system calls and it gives all the information of the provenance.

## Bigger Objective ##

This is a part of the program for system call alignment. System call alignment provides an evidence of two executions that their executions are the same, otherwise, only output is the sole evidence, which is usually far from enough.  
Not only will the system call alignment provides an evidence for whether the two executions were the same, but it also gives out information of where the executions branched off differently through the use of control flow graphs (CFGs), which are emitted through the use of source codes and LLVM. This is to help user detect the cause of the differences.  
We use system calls as the instructions to look into because system calls are instructions that provides information of provenance. Sciunit, the other project in our lab, also looks into the provenance for capturing what files are necessary for the creation of containers to reproduce the execution, so it makes sense for us to investigate system calls instead of other types of instructions.  
The system call alignment is composed of 3 steps:  
1. Emission of CFGs (in dotfiles) through the use of LLVM  
2. Simplification of the CFGs by omitting irrelevant instructions  
3. Path-finding using a system call trace of an execution and simplified CFGs  
4. Alignment comparing two paths found in step 3  

This repository has a program that does the step 2 in the system call alignment.

## Input ##
A directory with a set of dotfiles inside  
## Output ##
A directory with a set of files with information of CFGs, and each line represents a node.  
The lines are in the following format:  
id, type, (function name/ system call number,) number of oEdges, number of iEdges, number of bEdges, id of oEdge dests, id of iEdge srcs, id of bEdge dests  
For example, 
`0x970360,funccall,read,0,1,1,na,0x970310,0x970310`  
means  
```
id = 0x970360  
type = function call  
function name (because this is a function call node) = read  
number of outgoing edges = 0  
number of incoming edges = 1  
number of back edges = 1  
id of outgoing edge destinations = not applicable (because there isn't any)  
id of incoming edge sources = 0x970310  
id of back edge destinations = 0x970310  
```

## Procedure (At A High Level) ##  
1. Takes in the dotfiles with the function pydotplus\.graph\_from\_dot\_file  
2. Omits all the irrelevant instructions in the CFGs (i.e. instructions that are not system calls, function calls that leads to system calls, return calls)  
3. Omits all the vertices-LLVM basic blocks- that does not have instructions in them  
4. Makes the CFGs into one instructions per vertex  
5. Spits out the set of files (one file/function, one CFG is one function), in a specified format  
