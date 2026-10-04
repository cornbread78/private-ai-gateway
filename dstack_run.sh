#!/data/data/com.termux/files/usr/bin/sh
# Unset any global preloads from the interactive shell
unset LD_PRELOAD

# Use LD_LIBRARY_PATH instead of LD_PRELOAD if possible, or invoke python 
# with environment dictionary modification so subprocesses don't inherit it.
env -u LD_PRELOAD \
    PYTHONPATH="$PREFIX/lib/python3.13/site-packages" \
    python3 -c "
import os, sys, ctypes
try:
    # Load libpython explicitly into memory using ctypes with RTLD_GLOBAL
    lib_path = os.path.join(os.environ.get('PREFIX', '/data/data/com.termux/files/usr'), 'lib', 'libpython3.13.so')
    ctypes.CDLL(lib_path, mode=ctypes.RTLD_GLOBAL)
except Exception:
    pass

from dstack._internal.cli.main import main
sys.argv = ['dstack', 'apply', '-f', 'compose.yaml']
main()
"
