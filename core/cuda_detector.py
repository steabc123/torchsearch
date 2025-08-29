import subprocess
import re

def get_nvcc_version():
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, check=True)
        match = re.search(r'release (\d+\.\d+)', result.stdout)
        return match.group(1) if match else None
    except (subprocess.CalledProcessError, FileNotFoundError, Exception):
        return None