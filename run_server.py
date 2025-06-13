import subprocess

commands = [
    ["py", "-3.9", "server/sc_server.py"],
    ["py", "-3.9", "server/rc_server.py"],
    ["py", "-3.9", "server/dc_server.py"],
    ["py", "-3.9", "prover/prover_sc_to_rc.py"],
    ["py", "-3.9", "prover/prover_rc_to_dc.py"],
]

procs = [subprocess.Popen(cmd) for cmd in commands]

try:
    for p in procs:
        p.wait()
except KeyboardInterrupt:
    for p in procs:
        p.terminate()
