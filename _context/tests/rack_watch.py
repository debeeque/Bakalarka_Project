import json
import subprocess
import sys
import time

sys.path.insert(0, "/home/muk0015/diploma_project")
import results

NS, IF = "analyzer_monitor", "mon0"
OWN = "00:e0:4c:68:02:01,00:e0:4c:68:02:23"
LOG = open("/tmp/rack_watch.log", "a", buffering=1)


def log(t):
    LOG.write(time.strftime("%H:%M:%S ") + t + "\n")


def carrier():
    r = subprocess.run(["sudo", "ip", "netns", "exec", NS, "cat", "/sys/class/net/%s/carrier" % IF],
                       capture_output=True, text=True)
    return r.stdout.strip() == "1"


def listen(extra, t):
    cmd = ["sudo", "ip", "netns", "exec", NS, "python3", "/home/muk0015/diploma_project/l2_listen.py", IF,
           "-t", str(t), "--all", "--own", OWN] + extra
    out = subprocess.run(cmd, capture_output=True, text=True, cwd="/home/muk0015/diploma_project").stdout
    res = results.parse_result(out, "l2_listen")
    for line in out.splitlines():
        if not line.startswith("RESULT"):
            log("  " + line)
    if res is not None:
        res["output"] = out.splitlines()[-60:]
        log("saved " + results.save("l2_listen.py", IF, res))
    return res or {}


log("start: waiting for the PC cable to be pulled")
while carrier():
    time.sleep(0.5)
log("no link: waiting for the switch")
t0 = time.time()
while not carrier():
    if time.time() - t0 > 900:
        log("no link in 15 min, giving up")
        sys.exit(0)
    time.sleep(0.5)
log("LINK UP after %.0f s" % (time.time() - t0))
time.sleep(2)
pi = subprocess.run(["sudo", "ip", "netns", "exec", NS, "python3", "/home/muk0015/diploma_project/port_info.py", IF],
                    capture_output=True, text=True, cwd="/home/muk0015/diploma_project").stdout
for line in pi.splitlines():
    if not line.startswith("RESULT"):
        log("  " + line)
r = results.parse_result(pi, "port_info")
if r:
    log("saved " + results.save("port_info.py", IF, r))
cap = subprocess.Popen(["sudo", "ip", "netns", "exec", NS, "timeout", "150", "tcpdump", "-i", IF, "-U", "-w",
                        "/home/muk0015/results/%s/%s_rack_mon0.pcap" % (time.strftime("%Y%m%d"), time.strftime("%H%M%S"))],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
log("listening 65 s, sending nothing")
res = listen([], 65)
if not res.get("neighbors"):
    log("nothing heard: HELLO and listening 40 s more")
    listen(["--hello"], 40)
cap.wait()
log("DONE")
