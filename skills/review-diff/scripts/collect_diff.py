import subprocess
p = subprocess.run(["git","diff"], text=True, capture_output=True)
print((p.stdout or p.stderr)[:12000])
