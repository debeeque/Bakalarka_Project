#!/usr/bin/env python3
# KP7 of the TRAFFIC screen: the feed shows the same addresses, protocol and length as tcpdump -n
# for 20 consecutive packets. Slow traffic so that every packet reaches the feed.
# Run on the device as root, DHCP/RA on, loop snd0 <-> mon0.
import json
import re
import subprocess
import sys
import time

PCAP = "/tmp/feed_check.pcap"
MON = ["ip", "netns", "exec", "analyzer_monitor"]
SND = ["ip", "netns", "exec", "analyzer_sender"]


def main():
    out = subprocess.run(["ip", "-n", "analyzer_monitor", "-6", "-o", "addr", "show", "mon0"],
                         capture_output=True, text=True).stdout
    t6 = [w.split("/")[0] for w in out.split() if w.startswith("fd00:2::")][0]
    cap = subprocess.Popen(MON + ["python3", "/home/muk0015/diploma_project/sniff_stats.py", "mon0", "--pcap", PCAP,
                                  "--duration", "26", "--feed", "8"], stdout=subprocess.PIPE, text=True)
    time.sleep(1.5)
    gen = subprocess.Popen(SND + ["sh", "-c", "ping -6 -i 1 -c 20 %s >/dev/null & "
                                  "python3 /home/muk0015/diploma_project/pkt_gen.py snd0 --proto arp --dst 10.0.2.20 "
                                  "--count 10 --rate 0.5 >/dev/null 2>&1 & wait" % t6])
    lines = cap.communicate()[0].splitlines()
    gen.wait()
    feed = {}
    for ln in lines:
        if ln.startswith("STATS "):
            for p in json.loads(ln[6:])["feed"]:
                feed[p["n"]] = p
    dump = subprocess.run(["tcpdump", "-r", PCAP, "-n", "-e", "-tt"], capture_output=True, text=True).stdout.splitlines()
    rows = []
    for i, ln in enumerate(dump, 1):
        m = re.search(r"length (\d+): (.*)", ln)
        length = int(m.group(1)) if m else -1
        rest = m.group(2) if m else ""
        if "ethertype ARP" in ln:
            cat = "ARP"
            a = re.search(r"tell (\S+?),", rest)
            b = re.search(r"who-has (\S+)", rest)
            src, dst = (a.group(1) if a else ""), (b.group(1) if b else "")
        else:
            a = re.search(r"^(\S+) > (\S+):\s", rest)
            src, dst = (a.group(1), a.group(2)) if a else ("", "")
            cat = "ICMPv6" if "ICMP6" in rest else "ICMP" if "ICMP" in rest else \
                  "TCP" if re.search(r"Flags \[", rest) else "UDP" if "UDP" in rest else "other"
        rows.append((i, src, dst, cat, length))
    ok = checked = 0
    first = None
    for i, src, dst, cat, length in rows:
        p = feed.get(i)
        if p is None:
            continue
        first = first or i
        same = (p["src"], p["dst"], p["cat"], p["len"]) == (src, dst, cat, length)
        checked += 1
        ok += same
        print("#%-3d feed %-10s %-26s > %-26s %4d | tcpdump %-6s %s > %s %d  %s" % (
            i, p["cat"], p["src"], p["dst"], p["len"], cat, src, dst, length, "OK" if same else "DIFF"))
        if checked == 20:
            break
    print("pcap packets %d, in feed %d, checked %d, equal %d" % (len(rows), len(feed), checked, ok))
    return 0 if checked == 20 and ok == 20 else 1


if __name__ == "__main__":
    sys.exit(main())
