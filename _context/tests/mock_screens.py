import os
import subprocess
import sys
import tkinter as tk

sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else "/tmp/newgui")
import gui_app
from ui_kit import G, H, M, W

OUT = "/tmp/shots"
os.makedirs(OUT, exist_ok=True)

SPEED_LOG = """------------------------------------------------------------
01:12:04  iperf3 TCP v6 to fd00:2::2e0:4cff:fe68:201
Target: fd00:2::2e0:4cff:fe68:201 (discovered)
Connecting to host fd00:2::2e0:4cff:fe68:201, port 5201
[  5] local fd00:2::10 port 49152 connected to fd00:2::2e0:4cff:fe68:201 port 5201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  18.0 MBytes   151 Mbits/sec    0    312 KBytes
[  5]   1.00-2.00   sec  17.9 MBytes   150 Mbits/sec    0    312 KBytes
[  5]   2.00-3.00   sec  17.9 MBytes   150 Mbits/sec    0    312 KBytes
[  5]   3.00-4.00   sec  17.9 MBytes   150 Mbits/sec    0    312 KBytes
[  5]   4.00-5.00   sec  17.9 MBytes   150 Mbits/sec    0    312 KBytes
- - - - - - - - - - - - - - - - - - - - - - - - -
[  5]   0.00-5.00   sec  89.6 MBytes   150 Mbits/sec    0             sender
[  5]   0.00-5.00   sec  89.4 MBytes   150 Mbits/sec                  receiver"""

RA_LOG = """=== IPv6 Router Advertisement audit ===
Interface    : snd0 (00:e0:4c:68:02:23)
Solicitation : sent to ff02::2 from fe80::2e0:4cff:fe68:223
Routers      : 1

--- Router 1 [OWN DEVICE] ---
Source       : fe80::2e0:4cff:fe68:201
Flags        : M=1 O=1   preference=Medium
Router life  : 1800 s
Prefix       : fd00:1::/64   L=1 A=1 R=0
MTU          : 1500
Audit:
  [OK   ] another port of this device, received over the wire
  [WARN ] M flag set together with A flag, mixed DHCPv6 and SLAAC"""

NMAP_LOG = """Nmap 10.0.1.20 on mon0
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 10.0.1.20
Host is up (0.0011s latency).
Not shown: 98 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 10.0 (protocol 2.0)
8080/tcp open  http    SimpleHTTPServer 0.6 (Python 3.13.5)"""


def fill(app):
    app.note("SPEED", "PASS", " 150 Mbit/s", " v6")
    app.note("SCAN", "PASS", " 2 neighbours", "")
    app.note("IPv6", "PASS", " 1 router", "")
    app.note("PATH", "PASS", " 4/4, 1.0 ms", "")
    app.found = {"mon0": {"v4": "10.0.1.20", "v6": "fd00:1::2e0:4cff:fe68:223"},
                 "snd0": {"v6": "fd00:2::2e0:4cff:fe68:201"}}
    app.scan_target = "10.0.1.20"


def rects(widget):
    out = []
    for w in widget.winfo_children():
        if getattr(w, "role", None) and w.winfo_ismapped():
            name = w.cget("text").replace("\n", " ") if isinstance(w, tk.Button) else "tile"
            out.append((w.role, w.winfo_rootx(), w.winfo_rooty(), w.winfo_width(), w.winfo_height(), name))
        out += rects(w)
    return out


def check(name, frame):
    rs = rects(frame)
    bad = []
    for role, x, y, w, h, n in rs:
        need = 80 if role == "main" else 60
        if (role == "main" and (w < need or h < need)) or (role != "main" and min(w, h) < need):
            bad.append("U1 %s %dx%d < %d" % (n, w, h, need))
        if x < M or y < M or x + w > W - M or y + h > H - M:
            bad.append("U2 edge %s" % n)
    for i, a in enumerate(rs):
        for b in rs[i + 1:]:
            dx = max(b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]))
            dy = max(b[2] - (a[2] + a[4]), a[2] - (b[2] + b[4]))
            if max(dx, dy) < G:
                bad.append("U2 gap %d: %s / %s" % (max(dx, dy), a[5], b[5]))
    print("%-8s tappable %2d  violations %d %s" % (name, len(rs), len(bad), "; ".join(bad)), flush=True)


def main():
    root = tk.Tk()
    app = gui_app.AnalyzerApp(root)
    app.unlock()
    fill(app)
    plan = [("home", "HOME", None), ("speed", "SPEED", lambda s: (s.select_port("snd0"), s.log(SPEED_LOG),
                                                                    s.set_verdict("PASS", "150 Mbit/s  TCP v6, snd0"))),
            ("scan", "SCAN", lambda s: (s.log(NMAP_LOG), s.running("nmap", None),
                                        s.set_verdict("RUNNING", "Nmap 10.0.1.20 on mon0, 12 s"))),
            ("target", "TARGET", None), ("keypad", "KEYPAD", None),
            ("ipv6", "IPv6", lambda s: (s.select_port("snd0"), s.log(RA_LOG),
                                        s.set_verdict("PASS", "1 router, this device on snd0"))),
            ("path", "PATH", lambda s: s.set_verdict("PASS", "4/4 replies, avg 1.0 ms  ping v6, mon0")),
            ("dhcp", "DHCP / RA", None), ("system", "SYSTEM", None)]

    def step(i):
        if i == len(plan):
            root.destroy()
            return
        shot, name, prep = plan[i]
        if name == "HOME":
            app.home()
        else:
            app.open(name)
        if prep:
            prep(app.screens[name])
        root.update_idletasks()

        def snap():
            check(shot, app.screens[name])
            subprocess.run(["scrot", "-o", os.path.join(OUT, "p03_%s.png" % shot)])
            step(i + 1)

        root.after(900, snap)

    root.after(1500, step, 0)
    root.mainloop()


if __name__ == "__main__":
    main()
