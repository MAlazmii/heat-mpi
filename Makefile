CC = cc
MPICC = mpicc
CFLAGS = -O3 -std=c11 -Wall -Wextra -Wpedantic -Wconversion -Wshadow -Werror
LDLIBS = -lm
.PHONY: all test clean sanitize
all: build/heat_serial build/heat_mpi
build:
	mkdir -p build
build/heat_serial: src/heat.c Makefile scripts/compile.py | build
	python3 scripts/compile.py $@ $(CC) $(CFLAGS) $< -o $@ $(LDLIBS)
build/heat_mpi: src/heat.c Makefile scripts/compile.py | build
	python3 scripts/compile.py $@ $(MPICC) $(CFLAGS) -DUSE_MPI $< -o $@ $(LDLIBS)
test: all
	python3 -m unittest discover -s tests -v
sanitize: | build
	$(CC) -O1 -g -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer src/heat.c -o build/heat_sanitize -lm
	./build/heat_sanitize 7 5 20 impulse
	./build/heat_sanitize 1 1 0 sine
clean:
	rm -rf build
