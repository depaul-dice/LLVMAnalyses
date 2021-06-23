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


