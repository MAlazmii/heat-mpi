/* Explicit diffusion on a unit square. See docs/numerics.md for the contract. */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#ifdef USE_MPI
#include <mpi.h>
#endif

static int rank_id = 0;
static void fail(const char *message) {
    fprintf(stderr, "rank %d: %s\n", rank_id, message);
#ifdef USE_MPI
    MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
#endif
    exit(EXIT_FAILURE);
}
#ifdef USE_MPI
#define CHECK(call) do { if ((call) != MPI_SUCCESS) fail("MPI operation failed: " #call); } while (0)
#endif
static int number(const char *text, int minimum, int maximum) {
    char *end = NULL;
    errno = 0;
    if (!*text || *text < '0' || *text > '9') fail("expected unsigned decimal integer");
    long value = strtol(text, &end, 10);
    if (errno || *end || value < minimum || value > maximum) fail("integer outside supported range");
    return (int)value;
}
static void *allocate(size_t count, size_t width) {
    if (count > SIZE_MAX / width) fail("allocation size overflow");
    void *memory = calloc(count, width);
    if (!memory) fail("allocation failed");
    return memory;
}
static double seconds(void) {
#ifdef USE_MPI
    return MPI_Wtime();
#else
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t)) fail("clock failed");
    return (double)t.tv_sec + 1e-9 * (double)t.tv_nsec;
#endif
}
static int rows_for(int ny, int size, int r) { return ny / size + (r < ny % size); }
static int offset_for(int ny, int size, int r) { return r*(ny/size) + (r < ny%size ? r : ny%size); }

int main(int argc, char **argv) {
    int size = 1;
#ifdef USE_MPI
    if (MPI_Init(&argc, &argv) != MPI_SUCCESS) return EXIT_FAILURE;
    CHECK(MPI_Comm_set_errhandler(MPI_COMM_WORLD, MPI_ERRORS_RETURN));
    CHECK(MPI_Comm_rank(MPI_COMM_WORLD, &rank_id));
    CHECK(MPI_Comm_size(MPI_COMM_WORLD, &size));
#endif
    if (argc < 5 || argc > 6) fail("usage: heat NX NY STEPS sine|impulse [new-field.csv|-]");
    int nx = number(argv[1], 1, 100000), ny = number(argv[2], 1, 100000);
    int steps = number(argv[3], 0, 100000000);
    if ((size_t)nx * (size_t)ny > 10000000) fail("grid exceeds 10 million interior cells");
    if (size > ny) fail("rank count must not exceed NY");
    int sine = strcmp(argv[4], "sine") == 0;
    if (!sine && strcmp(argv[4], "impulse") != 0) fail("initial condition must be sine or impulse");
    int export = argc == 6 && strcmp(argv[5], "-") != 0;
    FILE *output = NULL;
    if (rank_id == 0 && export) {
        output = fopen(argv[5], "wx");
        if (!output) fail("cannot create output (exists or directory unavailable)");
    }
    int rows = rows_for(ny, size, rank_id), offset = offset_for(ny, size, rank_id);
    size_t stride = (size_t)nx + 2, cells = ((size_t)rows + 2) * stride;
    double *a = allocate(cells, sizeof(double)), *b = allocate(cells, sizeof(double));
    double dx = 1.0/(nx+1), dy = 1.0/(ny+1);
    double dt = 0.2/(1/(dx*dx)+1/(dy*dy)), rx = dt/(dx*dx), ry = dt/(dy*dy);
    double pi = acos(-1.0);
    for (int y=1; y<=rows; ++y)
        for (int x=1; x<=nx; ++x)
            a[(size_t)y*stride+(size_t)x] = sine ? sin(pi*x*dx)*sin(pi*(offset+y)*dy) : (double)(x-1==nx/2 && offset+y-1==ny/2);
#ifdef USE_MPI
    int up = rank_id == 0 ? MPI_PROC_NULL : rank_id-1;
    int down = rank_id == size-1 ? MPI_PROC_NULL : rank_id+1;
    CHECK(MPI_Barrier(MPI_COMM_WORLD));
#endif
    double start = seconds();
    for (int step=0; step<steps; ++step) {
#ifdef USE_MPI
        CHECK(MPI_Sendrecv(a+stride+1,nx,MPI_DOUBLE,up,0,
                          a+((size_t)rows+1)*stride+1,nx,MPI_DOUBLE,down,0,MPI_COMM_WORLD,MPI_STATUS_IGNORE));
        CHECK(MPI_Sendrecv(a+(size_t)rows*stride+1,nx,MPI_DOUBLE,down,1,
                          a+1,nx,MPI_DOUBLE,up,1,MPI_COMM_WORLD,MPI_STATUS_IGNORE));
#endif
        for (int y=1; y<=rows; ++y) {
            for (int x=1; x<=nx; ++x) {
                size_t i=(size_t)y*stride+(size_t)x;
                b[i]=a[i]+rx*(a[i-1]-2*a[i]+a[i+1])+ry*(a[i-stride]-2*a[i]+a[i+stride]);
            }
        }
        double *swap=a; a=b; b=swap;
    }
    double elapsed = seconds()-start;
#ifdef USE_MPI
    double slowest = 0;
    CHECK(MPI_Reduce(&elapsed,&slowest,1,MPI_DOUBLE,MPI_MAX,0,MPI_COMM_WORLD));
    elapsed=slowest;
#endif
    double local_error=0;
    int invalid=0;
    for (int y=1; y<=rows; ++y) for (int x=1; x<=nx; ++x) {
        double value=a[(size_t)y*stride+(size_t)x];
        if (!isfinite(value)) invalid=1;
        if (sine) {
            double exact=exp(-2*pi*pi*steps*dt)*sin(pi*x*dx)*sin(pi*(offset+y)*dy);
            local_error=fmax(local_error,fabs(value-exact));
        }
    }
#ifdef USE_MPI
    CHECK(MPI_Allreduce(MPI_IN_PLACE,&invalid,1,MPI_INT,MPI_MAX,MPI_COMM_WORLD));
    CHECK(MPI_Allreduce(MPI_IN_PLACE,&local_error,1,MPI_DOUBLE,MPI_MAX,MPI_COMM_WORLD));
#endif
    if (invalid) fail("nonfinite result");
    if (export) {
        double *packed=allocate((size_t)rows*(size_t)nx,sizeof(double));
        for (int y=0;y<rows;++y) memcpy(packed+(size_t)y*(size_t)nx,a+((size_t)y+1)*stride+1,(size_t)nx*sizeof(double));
        double *global=NULL;
        if (rank_id==0) global=allocate((size_t)nx*(size_t)ny,sizeof(double));
#ifdef USE_MPI
        int *counts=allocate((size_t)size,sizeof(int)), *offsets=allocate((size_t)size,sizeof(int));
        for (int r=0;r<size;++r) { counts[r]=rows_for(ny,size,r)*nx; offsets[r]=offset_for(ny,size,r)*nx; }
        CHECK(MPI_Gatherv(packed,rows*nx,MPI_DOUBLE,global,counts,offsets,MPI_DOUBLE,0,MPI_COMM_WORLD));
        free(counts); free(offsets);
#else
        memcpy(global,packed,(size_t)nx*(size_t)ny*sizeof(double));
#endif
        if (rank_id==0) {
            if (fprintf(output,"x,y,u\n")<0) fail("output write failed");
            for (int y=0;y<ny;++y) for (int x=0;x<nx;++x)
                if (fprintf(output,"%d,%d,%.17g\n",x,y,global[(size_t)y*(size_t)nx+(size_t)x])<0) fail("output write failed");
            if (fclose(output)) fail("output close failed");
        }
        free(global); free(packed);
    }
    if (rank_id==0) {
        printf("{\"nx\":%d,\"ny\":%d,\"steps\":%d,\"ranks\":%d,\"dt\":%.17g,\"seconds\":%.17g,\"continuum_linf\":",nx,ny,steps,size,dt,elapsed);
        if (sine) printf("%.17g",local_error); else printf("null");
        puts("}");
    }
    free(a); free(b);
#ifdef USE_MPI
    CHECK(MPI_Finalize());
#endif
    return EXIT_SUCCESS;
}
