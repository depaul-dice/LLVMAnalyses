# SIMPLIFIER 

This is a program that takes in a set of dotfiles that are created with the llvm bitcode.
The program's objective is to simplify the graphs that would only have instructions that are relevant to system calls. System calls are chosen because [Sciunit](sciunit.run) keeps track of system calls and it gives all the information of the provenance.


