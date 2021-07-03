
# HOW TO GET DOTFILES #

Before going into the simplifying of the dotfiles, we first need to use LLVM to access the source code and emit llvm bitcode and dotfiles which represents each function. In this directory, we will use the helloworld example and Makefile to show the procedure. 

clam-prov is a private repository in SRI, so it is not accessible to everyone yet.

The helloworld example is given in the directory helloworld with a makefile.

### WARNING ###

Dotfiles can be created without clam, but it doesn't do the devirtualization, meaning if the function calls are called with function ptr, the call is on the function ptr, which makes it enormously harder to see which function it went to in the path finding phase.

# STEPS #

1. Install `wllvm` as a compiler
2. Compile MUSLLVM and get libc.a libc.a.bc crt1.o
3. Compile and install clam-prov
4. Move the libc.a libc.a.bc crt1.o to the directory you want to make the dotfiles and executables
5. (Assuming the helloworld.c is the c file,) Compile with
    ```
    wllvm helloworld.c libc.a -o helloworld
    ```
6. Create the bitcode with `extract-bc`
    ```
    extract-bc -b helloworld
    ```
7. Create devirtualized bitcode with `clam-pp`
    ```
    clam-pp -crab-devirt --devirt-resolver=sea-dsa --sea-dsa-type-aware=false helloworld.bc -o helloworld.pp.bc
    ```
8. Create dotfiles with dot `--opt-cfg`
    ```
    dot --opt-cfg helloworld.pp.bc
    ```
9. You can create the executable in by using libc.a libc.a.bc crt1.o, you need to link libgcc.a to create the binary. Use
    ```
    locate libgcc.a
    ``` 
    to find where the file exists. 
