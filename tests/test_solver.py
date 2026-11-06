"""Executable-level checks with mathematical and independent small-grid oracles."""
import csv
import json
import math
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MPI = shlex.split(os.environ.get('MPIEXEC', 'mpiexec'))
ENV = dict(os.environ, OMPI_MCA_rmaps_base_oversubscribe='1')

class SolverTests(unittest.TestCase):
    def run_solver(self, nx, ny, steps, mode='sine', ranks=0, extra=None):
        binary = ROOT / 'build' / ('heat_mpi' if ranks else 'heat_serial')
        self.assertTrue(binary.is_file(), f'Missing solver: {binary}')
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'field.csv'
            cmd = ([*MPI, '-n', str(ranks)] if ranks else []) + [str(binary), str(nx), str(ny), str(steps), mode, str(output)]
            run = subprocess.run(cmd + (extra or []), text=True, capture_output=True, env=ENV, timeout=30)
            self.assertEqual(run.returncode, 0, run.stderr)
            report=json.loads(run.stdout)
            self.assertEqual(report['ranks'],ranks or 1, 'launcher did not form the requested communicator')
            with output.open() as f:
                rows = list(csv.DictReader(f))
            return [float(row['u']) for row in rows]

    def test_discrete_sine_eigenmode(self):
        # Detects wrong coefficient, timestep, coordinate or number of updates.
        for ranks in (0, 1, 2, 3, 4):
            nx, ny, steps = 7, 5, 11
            dt = .2 / ((nx+1)**2 + (ny+1)**2)
            decay = 1 - 4*dt*((nx+1)**2*math.sin(math.pi/(2*(nx+1)))**2 + (ny+1)**2*math.sin(math.pi/(2*(ny+1)))**2)
            expected = [math.sin(math.pi*(x+1)/(nx+1))*math.sin(math.pi*(y+1)/(ny+1))*decay**steps for y in range(ny) for x in range(nx)]
            actual = self.run_solver(nx, ny, steps, ranks=ranks)
            self.assertLess(max(abs(a-b) for a,b in zip(actual,expected,strict=True)), 2e-14)

    def test_impulse_reference_and_small_slabs(self):
        # Independent dictionary implementation catches incorrect halo exchange.
        for nx,ny in ((1,1),(2,4),(7,5),(3,4)):
            dt = .2 / ((nx+1)**2+(ny+1)**2)
            grid = {(x,y): float((x,y)==(nx//2,ny//2)) for y in range(ny) for x in range(nx)}
            for steps in range(4):
                expected = [grid[x,y] for y in range(ny) for x in range(nx)]
                for ranks in (0,1, min(2,ny), min(4,ny)):
                    actual = self.run_solver(nx,ny,steps,'impulse',ranks)
                    self.assertLess(max(abs(a-b) for a,b in zip(actual,expected,strict=True)),1e-14)
                    self.assertGreaterEqual(min(actual),0)
                grid = {(x,y): v+dt*((nx+1)**2*(grid.get((x-1,y),0)-2*v+grid.get((x+1,y),0))+(ny+1)**2*(grid.get((x,y-1),0)-2*v+grid.get((x,y+1),0))) for (x,y),v in grid.items()}

    def test_continuum_convergence(self):
        errors=[]
        # Refinement with dt reduced by four, at equal physical final time.
        for n,steps in ((15,16),(31,64)):
            values=self.run_solver(n,n,steps)
            t=steps*.2/(2*(n+1)**2)
            exact=[math.exp(-2*math.pi**2*t)*math.sin(math.pi*(x+1)/(n+1))*math.sin(math.pi*(y+1)/(n+1)) for y in range(n) for x in range(n)]
            errors.append(max(abs(a-b) for a,b in zip(values,exact,strict=True)))
        self.assertGreater(errors[0]/errors[1],3.8)
        self.assertLess(errors[0]/errors[1],4.2)

    def test_reject_invalid_inputs(self):
        for ranks in (0,2):
            binary=ROOT/'build'/('heat_mpi' if ranks else 'heat_serial')
            self.assertTrue(binary.exists())
            for args in (['0','4','1','sine'], ['-1','4','1','sine'], ['2junk','4','1','sine'], ['2','4','-1','sine'], ['2','4','1','bad'], ['999999999999999999999','4','1','sine'], ['100000','100000','1','sine'], ['2','4','1','sine','-','extra']):
                cmd=([*MPI,'-n',str(ranks)] if ranks else [])+[str(binary),*args]
                run=subprocess.run(cmd,capture_output=True,env=ENV,timeout=20)
                self.assertNotEqual(run.returncode,0,args)
        run=subprocess.run([*MPI,'-n','2',str(ROOT/'build/heat_mpi'),'2','1','1','sine'],capture_output=True,env=ENV,timeout=20)
        self.assertNotEqual(run.returncode,0)

    def test_output_failure_and_collision(self):
        for ranks in (0,2):
            with tempfile.TemporaryDirectory() as tmp:
                p=Path(tmp)/'existing.csv'; p.write_text('keep me')
                for target in (str(p),str(Path(tmp)/'absent'/'field.csv')):
                    cmd=([*MPI,'-n',str(ranks)] if ranks else [])+[str(ROOT/'build'/('heat_mpi' if ranks else 'heat_serial')),'3','4','2','sine',target]
                    run=subprocess.run(cmd,capture_output=True,env=ENV,timeout=20)
                    self.assertNotEqual(run.returncode,0)
                self.assertEqual(p.read_text(),'keep me')

if __name__=='__main__': unittest.main(verbosity=2)
