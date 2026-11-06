import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
class BuildManifestTests(unittest.TestCase):
    def test_records_real_compiler_and_artifact(self):
        wrapper=ROOT/'scripts/compile.py'
        self.assertTrue(wrapper.is_file(), 'missing compiler provenance wrapper')
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'main.c'; src.write_text('int main(void) {return 0;}\n')
            binary=Path(tmp)/'program'
            cmd=['cc','-std=c11',str(src),'-o',str(binary)]
            subprocess.run(['python3',str(wrapper),str(binary),*cmd],check=True,capture_output=True,timeout=30)
            data=json.loads(Path(str(binary)+'.json').read_text())
            self.assertEqual(data['command'],cmd)
            self.assertEqual(data['binary_sha256'],hashlib.sha256(binary.read_bytes()).hexdigest())
            self.assertIn('clang',data['compiler_version'].lower()) if __import__('sys').platform=='darwin' else self.assertTrue(data['compiler_version'])
