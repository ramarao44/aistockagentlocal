import os, glob, sys, runpy, traceback
root = r"C:\RAMARAO\Learning\AI\N8N\aistockagentlocal"
os.chdir(root)
sys.path.insert(0, root)
tests = sorted(glob.glob("scripts/test_*.py"))
print("FOUND", len(tests), "TEST SCRIPTS")
for f in tests:
    name = os.path.splitext(os.path.basename(f))[0]
    print("===", name, "===")
    try:
        runpy.run_module("scripts." + name, run_name="__main__")
        print("EXITCODE 0")
    except Exception:
        traceback.print_exc()
        print("EXITCODE 1")
