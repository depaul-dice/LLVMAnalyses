## Usage
python3 main.py directory 

## Input specification
The directory can only have the dotfiles inside

## Each files' Main Functionalities

### main.py
This file is the file to be run.
This file also deletes the irrelevant instructions in the basic blocks in LLVM dotfiles, and keeps track of the data that notifies the difference between before and after the simplification process.

### parseDot.py
This file contains the definition of the CFGs and vertices in the dotfiles. The parse\_dot function in the file parses the dotfile inputs into the CFGs and vertices that fit the definition in the file.

### simplify.py
This file has an implementation of further\_simplify which omits the redundant node.

## Inefficiency


## Limitations in Robustness
main.py cannot detect the difference of the function calls and arguments in the function calls, when it uses @ in the front. This is because the regular expression matching is not sophisticated enough to distinguish the two. The workaround is manually finding the pattern of the variable for each set of files as of now. 

## Definitions of Terminology
Redundant Node: the node that has at most one incoming edges and at most one outgoing edges (including back edges), which also has no instruction that are relevant to syscalls
