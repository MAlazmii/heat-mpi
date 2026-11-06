"""Failure diagnostics must survive subprocess errors in hosted checks."""
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import unittest

spec=importlib.util.spec_from_file_location('benchmark',Path(__file__).resolve().parents[1]/'scripts/benchmark.py')
benchmark=importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)

class BenchmarkFailureTests(unittest.TestCase):
    def test_failed_command_preserves_captured_diagnostics(self):
        error=io.StringIO()
        command=[sys.executable,'-c',"import sys; print('partial output'); print('halo diagnostic',file=sys.stderr); sys.exit(3)"]
        with contextlib.redirect_stderr(error), self.assertRaises(subprocess.CalledProcessError):
            benchmark.run(command)
        self.assertIn('halo diagnostic',error.getvalue())
        self.assertIn('partial output',error.getvalue())
