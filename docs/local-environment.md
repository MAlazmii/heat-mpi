# Local validation environment — 6 November 2026

The host is Apple Silicon, but installed Open MPI 5.0.6 is x86_64. Its default
Homebrew LLVM driver fails because it invokes an x86-only tool path against an
arm64-only libxcrun. No global installation or coursework files were changed.

The successful local build uses the native Apple clang driver to cross-compile
both binaries to x86_64, with the installed MPI include/library paths and explicit SDK:

```sh
make CC='/Library/Developer/CommandLineTools/usr/bin/clang -arch x86_64 -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk' \
 MPICC='/Library/Developer/CommandLineTools/usr/bin/clang -arch x86_64 -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk -I/usr/local/Cellar/open-mpi/5.0.6/include -L/usr/local/Cellar/open-mpi/5.0.6/lib -lmpi'
python3 -m unittest discover -s tests -v
make sanitize
```

Binaries therefore run under translation. This is local functionality evidence,
not representative HPC timing. Native arm64 serial AddressSanitizer/UBSan checks
use the default system compiler separately. MPI needs local sockets; a restricted
execution environment can block launch before the application starts.

For Linux or a cluster, use its matched native compiler/MPI toolchain and capture
fresh manifests/results. No cluster access, job submission, installation or spending
was performed. Benchmark files record actual executable formats and build commands.
