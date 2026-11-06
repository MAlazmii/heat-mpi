#!/usr/bin/env python3
"""Local fixed-workload timing; never a substitute for target-cluster measurements."""
import argparse
import csv
import math
import tempfile
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]

def run(cmd):
    try:
        return subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True,timeout=120,
            env=dict(os.environ,OMPI_MCA_rmaps_base_oversubscribe='1')).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        for output in (error.stdout, error.stderr):
            if output:
                print(output.decode(errors='replace') if isinstance(output,bytes) else output,file=sys.stderr)
        raise

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('output',type=Path,help='new results directory')
    parser.add_argument('--repeats',type=int,default=5)
    args=parser.parse_args()
    if args.repeats<3: parser.error('at least three repetitions required')
    args.output.mkdir(parents=True,exist_ok=False)
    # Validation is mandatory and failures prevent creation of benchmark evidence.
    validation=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,check=False,capture_output=True,text=True,timeout=180,env=dict(os.environ,OMPI_MCA_rmaps_base_oversubscribe='1'))
    (args.output/'validation.txt').write_text(validation.stdout+validation.stderr)
    validation.check_returncode()
    files=[p for directory in ('src','tests','scripts') for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    files += [ROOT/'Makefile', ROOT/'build/heat_serial', ROOT/'build/heat_mpi']
    builds={}
    for name in ('heat_serial','heat_mpi'):
        info=json.loads((ROOT/'build'/f'{name}.json').read_text())
        if info['binary_sha256']!=hashlib.sha256((ROOT/'build'/name).read_bytes()).hexdigest():
            raise ValueError('binary differs from recorded build')
        for path,checksum in info['source_sha256'].items():
            if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=checksum: raise ValueError('rebuild changed source')
        builds[name]=info
    metadata={'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'platform':platform.platform(),
        'machine':platform.machine(),'python':sys.version,
        'cpu':run(['sysctl','-n','machdep.cpu.brand_string']).strip() if sys.platform=='darwin' else platform.processor(),
        'validation':{'command':[sys.executable,'-m','unittest','discover','-s','tests','-v'],'exit_status':validation.returncode,'log':'validation.txt'},
        'rank_placement':'Options recorded in launcher; otherwise MPI defaults; local oversubscription allowed',
        'launcher':shlex.split(os.environ.get('MPIEXEC','mpiexec')),
        'translation_note':'Check executable_format against machine; x86_64 binaries on arm64 use translation.',
        'builds':builds,
        'mpi':run(shlex.split(os.environ.get('MPIEXEC','mpiexec'))+['--version']),
        'timing':'maximum rank loop duration, including halo exchange; excludes initialization, gathering and output',
        'scope':'local single machine; not multi-node scaling',
        'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    records=[]
    def checkpoint(status):
        temporary=args.output/'benchmark.tmp'
        temporary.write_text(json.dumps({'status':status,'metadata':metadata,'results':records},indent=2)+'\n')
        temporary.replace(args.output/'benchmark.json')
    checkpoint('incomplete')
    for ranks in (0,1,2,4):
        cmd=(shlex.split(os.environ.get('MPIEXEC','mpiexec'))+['-n',str(ranks)] if ranks else [])+[str(ROOT/'build'/('heat_mpi' if ranks else 'heat_serial')),'256','256','200','sine']
        # Validate the exact measured workload against the discrete sine eigenmode.
        with tempfile.TemporaryDirectory() as tmp:
            field=Path(tmp)/'field.csv'
            run(cmd+[str(field)])
            decay=1-.8*math.sin(math.pi/(2*257))**2
            with field.open() as f:
                errors=[abs(float(row['u'])-math.sin(math.pi*(int(row['x'])+1)/257)*math.sin(math.pi*(int(row['y'])+1)/257)*decay**200) for row in csv.DictReader(f)]
            if len(errors)!=256*256 or max(errors)>1e-12: raise ValueError('benchmark workload validation failed')
        run(cmd) # separate untimed warm-up run
        samples=[]
        record={'backend':'mpi' if ranks else 'serial','ranks':ranks or 1,'samples':samples}
        records.append(record)
        checkpoint('incomplete')
        for repeat in range(args.repeats):
            sample=json.loads(run(cmd)); sample.update(repeat=repeat,command=cmd)
            samples.append(sample)
            checkpoint('incomplete')
        times=[s['seconds'] for s in samples]
        record.update(median_seconds=statistics.median(times),min_seconds=min(times),max_seconds=max(times))
        checkpoint('incomplete')
    checkpoint('complete')
    print(args.output/'benchmark.json')

if __name__=='__main__': main()
