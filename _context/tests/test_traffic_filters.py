#!/usr/bin/env python3
# KP3 of the TRAFFIC screen: every filter preset lets through only its own traffic.
# Run on the device as root, DHCP/RA on, iperf3 server in analyzer_monitor, loop snd0 <-> mon0.
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, "/home/muk0015/diploma_project")
from traffic import FILTERS

OUT = "/tmp/ft"
MON = ["ip", "netns", "exec", "analyzer_monitor"]
SND = ["ip", "netns", "exec", "analyzer_sender"]
os.makedirs(OUT, exist_ok=True)


def target6():
    out = subprocess.run(["ip", "-n", "analyzer_monitor", "-6", "addr", "show", "mon0"],
                         capture_output=True, text=True).stdout
    m = re.search(r"(fd00:2::[0-9a-f:]+)/64", out)
    return m.group(1)


def generate(t6):
    d = "/home/muk0015/diploma_project"
    script = (
        "ping -6 -i 0.2 -c 30 {t6} >/dev/null 2>&1 & "
        "(sleep 1; iperf3 -c {t6} -t 2 -b 5M >/dev/null 2>&1; iperf3 -c {t6} -u -t 2 -b 1M >/dev/null 2>&1) & "
        "python3 {d}/pkt_gen.py snd0 --proto arp --dst 10.0.2.20 --count 5 --rate 5 >/dev/null 2>&1 & "
        "python3 {d}/pkt_gen.py snd0 --proto rs --count 2 --rate 1 >/dev/null 2>&1 & "
        "python3 {d}/pkt_gen.py snd0 --proto udp --dst {t6} --dport 53 --count 5 --rate 5 >/dev/null 2>&1 & "
        "nmap --script broadcast-dhcp-discover --script-args broadcast-dhcp-discover.timeout=3 -e snd0 "
        ">/dev/null 2>&1 & wait").format(t6=t6, d=d)
    return subprocess.Popen(SND + ["sh", "-c", script])


def count(pcap, expr=""):
    cmd = ["tcpdump", "-r", pcap, "-n"] + ([expr] if expr else [])
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    return len(out.splitlines())


def main():
    t6 = target6()
    host = t6
    print("target %s" % t6, flush=True)
    bad = 0
    for name, bpf, _ in FILTERS:
        if bpf is None:
            bpf = "host " + host
        pcap = os.path.join(OUT, name.replace(" / ", "_") + ".pcap")
        cmd = MON + ["python3", "/home/muk0015/diploma_project/sniff_stats.py", "mon0", "--pcap", pcap,
                     "--duration", "11"] + (["--bpf", bpf] if bpf else [])
        cap = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
        time.sleep(1.5)
        gen = generate(t6)
        out = cap.communicate()[0]
        gen.wait()
        res = json.loads(re.search(r"^RESULT sniff_stats (.*)$", out, re.M).group(1))
        cats = {k: v[0] for k, v in res["cats"].items() if v[0]}
        total = count(pcap)
        stray = count(pcap, "not (%s)" % bpf) if bpf else 0
        ok = total == res["packets"] and stray == 0 and total > 0
        bad += not ok
        print("%-8s %-58s packets %5d pcap %5d stray %d  %s  %s" % (
            name, bpf or "(none)", res["packets"], total, stray, cats, "OK" if ok else "FAIL"), flush=True)
    print("presets failed: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
