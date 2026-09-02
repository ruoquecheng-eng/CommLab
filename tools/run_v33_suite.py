from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    raise SystemExit(subprocess.call([sys.executable,str(ROOT/'experiments'/'run_v33_suite.py')],cwd=ROOT))
