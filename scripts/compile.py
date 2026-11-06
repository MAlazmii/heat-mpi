#!/usr/bin/env python3
"""Compile and bind the actual command/toolchain to its resulting executable."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    binary=Path(sys.argv[1]); command=sys.argv[2:]
    manifest=Path(str(binary)+'.json')
    manifest.unlink(missing_ok=True)
    subprocess.run(command,check=True,timeout=120)
    version=subprocess.run([command[0],'--version'],capture_output=True,text=True,check=True,timeout=20).stdout
    sources={str(Path(arg).resolve()):digest(Path(arg)) for arg in command if arg.endswith('.c') and Path(arg).is_file()}
    manifest.write_text(json.dumps({'command':command,'compiler_version':version,
        'compiler_environment':{k:os.environ[k] for k in ('OMPI_CC','SDKROOT','CPATH','LIBRARY_PATH') if k in os.environ},
        'source_sha256':sources,'binary_sha256':digest(binary),
        'executable_format':subprocess.run(['file',str(binary)],check=True,capture_output=True,text=True,timeout=10).stdout.strip()},indent=2)+'\n')
if __name__=='__main__': main()
