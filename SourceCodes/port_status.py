import json
import os
import subprocess
import sys
import threading
import time

PORTS = {"mon0": "analyzer_monitor", "snd0": "analyzer_sender"}
RUN = "/run/analyzer"
OUT = os.path.join(RUN, "ports.json")
DHCP_FLAG = os.path.join(RUN, "dhcp")
REFRESH_S = 10

changed = threading.Event()


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    except subprocess.SubprocessError:
        return None


def serving(dev):
    try:
        with open(os.path.join(RUN, "dnsmasq_%s.pid" % dev)) as f:
            os.kill(int(f.read().strip()), 0)
        return True
    except (OSError, ValueError):
        return False


def read_port(dev, ns):
    state = {"ns": ns, "present": False, "dhcp": serving(dev)}
    if not os.path.exists("/run/netns/" + ns):
        return state
    r = run(["ip", "-n", ns, "-j", "addr", "show", "dev", dev])
    if r is None or r.returncode != 0 or not r.stdout.strip():
        return state
    info = json.loads(r.stdout)[0]
    flags = info.get("flags", [])
    state.update(present=True, mac=info.get("address"), up="UP" in flags,
                 carrier="LOWER_UP" in flags, speed=None, duplex=None,
                 addr4=[], addr6=[])
    for a in info.get("addr_info", []):
        key = "addr4" if a.get("family") == "inet" else "addr6"
        state[key].append("%s/%s" % (a["local"], a["prefixlen"]))
    if state["carrier"]:
        base = "/sys/class/net/%s/" % dev
        r = run(["ip", "netns", "exec", ns, "cat", base + "speed", base + "duplex"])
        if r is not None and r.returncode == 0:
            lines = r.stdout.split()
            if len(lines) == 2 and lines[0].isdigit():
                state["speed"], state["duplex"] = int(lines[0]), lines[1]
    return state


def snapshot():
    data = {"time": time.time(), "dhcp": os.path.exists(DHCP_FLAG), "ports": {}}
    for dev, ns in PORTS.items():
        data["ports"][dev] = read_port(dev, ns)
    return data


def write(data):
    tmp = OUT + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    os.replace(tmp, OUT)


# One `ip monitor` per namespace; it exits when the namespace is deleted
def watch(ns):
    while True:
        if not os.path.exists("/run/netns/" + ns):
            time.sleep(1)
            continue
        try:
            proc = subprocess.Popen(["ip", "-n", ns, "monitor", "link", "address"],
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        except OSError:
            time.sleep(5)
            continue
        changed.set()
        for _ in proc.stdout:
            changed.set()
        proc.wait()
        changed.set()
        time.sleep(1)


def main():
    os.makedirs(RUN, exist_ok=True)
    for ns in PORTS.values():
        threading.Thread(target=watch, args=(ns,), daemon=True).start()
    last, last_flag, last_t = None, None, 0
    while True:
        fired = changed.wait(1)
        flag = os.path.exists(DHCP_FLAG)
        if not fired and flag == last_flag and time.monotonic() - last_t < REFRESH_S:
            continue
        changed.clear()
        time.sleep(0.2)
        last_flag, last_t = flag, time.monotonic()
        data = snapshot()
        key = json.dumps({k: v for k, v in data.items() if k != "time"}, sort_keys=True)
        if key != last:
            print(time.strftime("%H:%M:%S"), key, flush=True)
            last = key
        write(data)


if __name__ == "__main__":
    sys.exit(main())
