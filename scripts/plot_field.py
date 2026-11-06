#!/usr/bin/env python3
"""Generate a numerical illustration using actual serial solver output.
Optional dependency: matplotlib. Usage: python3 scripts/plot_field.py NEW.png
"""
import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
def main():
    output=Path(sys.argv[1])
    if output.exists(): raise FileExistsError(output)
    fig,axes=plt.subplots(1,2,figsize=(9,3.8),layout='constrained')
    with tempfile.TemporaryDirectory() as tmp:
        for ax,steps,title in zip(axes,(0,2000),('Initial temperature','After 2,000 steps'),strict=True):
            path=Path(tmp)/f'{steps}.csv'
            subprocess.run([str(ROOT/'build/heat_serial'),'63','47',str(steps),'sine',str(path)],check=True,capture_output=True,timeout=30)
            with path.open() as f: values=[float(row['u']) for row in csv.DictReader(f)]
            field=[values[y*63:(y+1)*63] for y in range(47)]
            im=ax.imshow(field,origin='lower',extent=(1/64,63/64,1/48,47/48),vmin=0,vmax=1,cmap='inferno',aspect='equal')
            ax.set(title=title,xlabel='x',ylabel='y')
        fig.colorbar(im,ax=axes,label='Temperature (dimensionless)',shrink=.85)
        fig.suptitle('Heat diffusion · fixed zero-temperature boundaries')
        fig.savefig(output,dpi=160)
    plt.close(fig)
if __name__=='__main__': main()
