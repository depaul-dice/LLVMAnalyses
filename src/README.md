## Usage ##
python3 main.py directory 

## Environment ##
- Ubuntu 16.04
- Python 3.7.8
- pydotplus 2.0.2

## Input specification ##
The directory can only have the dotfiles inside. 

## Each Files' Main Functionalities ##

### main.py ###
This file is the file to be run.
This file also deletes the irrelevant instructions in the basic blocks in LLVM dotfiles, and keeps track of the data that notifies the difference between before and after the simplification process.

### parseDot.py ###
This file contains the definition of the CFGs and vertices in the dotfiles. The parse\_dot function in the file parses the dotfile inputs into the CFGs and vertices that fit the definition in the file.

### simplify.py ### 
This file has an implementation of further\_simplify which omits the redundant node.

### tools.py ###
As of now it has only silent\_remove which removes the file without giving OSError even in the case of file not existing.

### oneInstG.py ###
This file converts the basic block (in LLVM context) and edges that creates the graph, which are created through the classes in parseDot.py, into one instruction per node CFGs. The reason for this change was for the simplification, but if it really simplifies the problem is another question.

### emptyFuncDetection.py ###
This file is no longer used but what it did was finding all the irrelevant functions that does not lead to system call for sure, and delete the instructions/nodes. The simplification is done after oneInstG conversion, but I decided to do it at once in simplify.py and main.py because it's just redundant.

## Inefficiency ##
I said in the emptyFuncDetection.py part, I took out the redundant simplification, but since it didn't make me omit all the nodes that were supposed to be omitted, if you look closely, I am actually doing the simplification of redundant node twice anyways. I have been too lazy to find the bug as of now, but if this inefficiency could be solved, it would be amazing...

### Inefficiency solved ###
This was not an inefficiency, it was a bug caused during the dicovery of back edges. I was deleting the incoming edges when the back edges were found, except I shouldn't have. It took me roughly 7 hours to find this bug. But now it's good.

## Limitations in Robustness ##
main.py cannot detect the difference of the function calls and arguments in the function calls, when it uses @ in the front. This is because the regular expression matching is not sophisticated enough to distinguish the two. The workaround is manually finding the pattern of the variable for each set of files as of now. 

## Definitions of Terminology ##
Redundant Node: the node that has at most one incoming edges and at most one outgoing edges (including back edges), which also has no instruction that are relevant to syscalls


