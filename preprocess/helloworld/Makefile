
dotfiles: helloworld.pp.bc 
	opt --dot-cfg $<

helloworld_static: helloworld.pp.bc crt1.o libc.a libc.a.bc
	clang -static -nostdlib $^ /usr/lib/gcc/x86_64-linux-gnu/7/libgcc.a -o $@

helloworld.pp.bc: helloworld.bc
	~/clam-prov/install/bin/clam-pp --crab-devirt --devirt-resolver=sea-dsa --sea-dsa-type-aware=false $< -o $@ 

helloworld.bc: helloworld 
	extract-bc -b $< 

helloworld: helloworld.c libc.a
	wllvm $< libc.a -o $@ 

.PHONY: clean
clean: 
	rm -f hello.o helloworld helloworld.bc helloworld.pp.bc .*.dot 
