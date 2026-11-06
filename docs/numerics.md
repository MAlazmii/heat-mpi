# Numerical specification and design

On (0,1)² solve u_t = u_xx + u_yy with homogeneous Dirichlet boundary conditions.
Use nx×ny interior points, dx=1/(nx+1), dy=1/(ny+1), and double precision.

Forward Euler with a centered five-point Laplacian:

u_new[i,j] = u[i,j] + rx*(u[i-1,j]-2u[i,j]+u[i+1,j])
                     + ry*(u[i,j-1]-2u[i,j]+u[i,j+1])

Set dt=0.2/(dx^-2+dy^-2), rx=dt/dx², ry=dt/dy². Thus rx+ry=0.2,
inside the 0.5 positivity/stability limit. The method is first order in time and
second order in space; refinement reduces dt with squared spacing.

For sine initialization, the continuum solution is
exp(-2π²t) sin(πx) sin(πy). The discrete sine mode has per-step amplitude factor
1-4rx sin²(π/(2(nx+1)))-4ry sin²(π/(2(ny+1))). Tests compare every interior value
to this independent closed form, and separately check convergence toward the PDE.
For impulse initialization, independent Python dictionary updates exercise halos
and rank boundaries. Small-test tolerances (1e-14 and 2e-14 absolute) allow rounding
while remaining far below errors caused by a missing update or halo exchange.
These tolerances are not prescribed for arbitrarily long/large runs.

Row slabs permit uneven partitions and contiguous communication without derived
datatypes. Blocking Sendrecv is the deliberately simple baseline. It avoids the
ordering hazards of separate blocking sends; buffers are disjoint, including
single-row partitions. See [Open MPI Sendrecv documentation](https://docs.open-mpi.org/en/main/man-openmpi/man3/MPI_Sendrecv.3.html).

This is fixed-step integration, not a steady-state convergence solver. Zero rows
per rank are rejected. Boundaries are fixed zero, not periodic. There is no claim
of energy/mass conservation: the domain loses heat through its boundary.

MPI failures abort the communicator. Allocation and output errors terminate the
whole job; failed output may leave a partial new file, which must not be treated
as a successful result. CSV uses integer indices, not physical coordinates.
