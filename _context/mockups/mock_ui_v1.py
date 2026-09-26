import subprocess
import sys
import tkinter as tk

W, H = 800, 480
M = 15
G = 8
BAR_H = 32
BTN_H = 80
BTN_Y = H - M - BTN_H
TOP = BAR_H + 8
BOTTOM = BTN_Y - 8
BACK_W = 110

C = {
    "bg": "#0E2226", "bar": "#06151A", "panel": "#15323A", "panel2": "#1D434C",
    "line": "#2A5862", "text": "#ECF3F4", "muted": "#9DBCC2", "dim": "#63858B",
    "good": "#66BB6A", "warn": "#FFB300", "bad": "#EF5350", "accent": "#4FC3F7",
    "back": "#455A64", "sel": "#0277BD",
}
PROTO = {"TCP": "#42A5F5", "UDP": "#AB47BC", "ICMP": "#FF7043",
         "ICMPv6": "#FFCA28", "ARP": "#26A69A", "other": "#78909C"}
SANS, MONO = "Liberation Sans", "DejaVu Sans Mono"
DOT, MID, ARR, ELL = chr(0x25CF), chr(0x00B7), chr(0x2192), chr(0x2026)
UP, DOWN, LEFT, RIGHT = chr(0x25B2), chr(0x25BC), chr(0x25C0), chr(0x25B6)

TAPS = []


def font(size, bold=False, family=SANS):
    return (family, -size, "bold") if bold else (family, -size)


def tap(widget, role):
    widget.role = role
    TAPS.append(widget)
    return widget


def button(parent, x, y, w, h, text, bg, role="main", size=18, fg="white"):
    b = tk.Button(parent, text=text, bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                  font=font(size, True), bd=0, highlightthickness=0, relief="flat")
    b.place(x=x, y=y, width=w, height=h)
    return tap(b, role)


def card(parent, x, y, w, h, title, sub, bg, accent=None, role="main", tsize=20, ssize=14,
         border=None):
    f = tk.Frame(parent, bg=bg, highlightthickness=3 if border else 0,
                 highlightbackground=border or bg)
    f.place(x=x, y=y, width=w, height=h)
    if accent:
        tk.Frame(f, bg=accent).place(x=0, y=0, width=6, relheight=1)
    tk.Label(f, text=title, font=font(tsize, True), fg=C["text"], bg=bg, anchor="w").place(x=16, y=10)
    tk.Label(f, text=sub, font=font(ssize), fg=C["muted"], bg=bg, anchor="nw", justify="left",
             wraplength=w - 28).place(x=16, y=14 + tsize + 6)
    return tap(f, role), f


def short(addr):
    if "::" not in addr:
        return addr
    head, tail = addr.split("::", 1)
    groups = tail.split(":")
    if len(groups) <= 2:
        return addr
    return head + "::" + ELL + ":".join(groups[-2:])


def status_bar(c, title):
    c.create_rectangle(0, 0, W, BAR_H, fill=C["bar"], width=0)
    y = BAR_H // 2 + 1
    c.create_text(M, y, text=title, font=font(17, True), fill=C["text"], anchor="w")
    x = 262
    for name, color in (("mon0 1000", C["good"]), ("snd0 1000", C["good"])):
        c.create_text(x, y, text=DOT, font=font(15), fill=color, anchor="w")
        c.create_text(x + 16, y, text=name, font=font(15), fill=C["text"], anchor="w")
        x += 102
    c.create_text(x, y, text="DHCP off", font=font(15), fill=C["dim"], anchor="w")
    c.create_text(x + 80, y, text="Wi-Fi Benswagin", font=font(15), fill=C["text"], anchor="w")
    bx = W - M - 40
    c.create_text(bx - 36, y, text="01:04", font=font(15, True), fill=C["text"], anchor="e")
    c.create_rectangle(bx - 26, y - 7, bx - 2, y + 7, outline=C["muted"], width=1)
    c.create_rectangle(bx - 2, y - 3, bx, y + 3, fill=C["muted"], width=0)
    c.create_rectangle(bx - 24, y - 5, bx - 24 + int(20 * 0.95), y + 5, fill=C["good"], width=0)
    c.create_text(W - M, y, text="95%", font=font(15), fill=C["text"], anchor="e")


def back(parent):
    button(parent, W - M - BACK_W, BTN_Y, BACK_W, BTN_H, "BACK", C["back"], role="secondary", size=17)


def bottom_bar(parent, items):
    widths = [w for _, w, _, _ in items]
    free = W - 2 * M - G * len(items) - BACK_W - sum(widths)
    grow = [i for i, it in enumerate(items) if it[3] == "main"]
    x = M
    for i, (text, w, bg, role) in enumerate(items):
        if i in grow:
            w += free // len(grow)
        button(parent, x, BTN_Y, w, BTN_H, text, bg, role=role, size=17)
        x += w + G
    back(parent)


def port_bar(parent, active, pause):
    bottom_bar(parent, [
        ("MON\nmon0", 92, C["sel"] if active == "mon0" else C["panel2"], "secondary"),
        ("SND\nsnd0", 92, C["sel"] if active == "snd0" else C["panel2"], "secondary"),
        ("STOP", 118, "#C62828", "main"),
        pause,
        ("FILTER", 108, "#00838F", "main"), ("SAVE", 100, "#2E7D32", "main"),
    ])


def screen():
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("%dx%d+0+0" % (W, H))
    root.attributes("-topmost", True)
    root.config(cursor="none", bg=C["bg"])
    c = tk.Canvas(root, width=W, height=H, bg=C["bg"], highlightthickness=0)
    c.place(x=0, y=0)
    return root, c


TILES = [
    ("AUTOTEST", "link, DHCP, IPv6, gateway, DNS, targets", ("PASS", C["good"], " 6/6, 14 s ago"), "#1E88E5"),
    ("TRAFFIC", "live capture, protocols, top talkers, PCAP", ("idle", C["muted"], ""), "#00ACC1"),
    ("GENERATOR", "ICMP, ICMPv6, UDP, TCP SYN, ARP, RS", ("snd0 " + ARR + " mon0", C["muted"], ""), "#00ACC1"),
    ("SPEED", "iperf3 TCP/UDP, v4/v6, frame sweep, server", ("276 Mbit/s", C["text"], " TCP v4"), "#1E88E5"),
    ("PORT", "speed, duplex, partner modes, LLDP, VLAN", ("1000 Full", C["good"], " both"), "#43A047"),
    ("SCAN", "ARP, IPv6 neighbours, Nmap", ("2 hosts", C["text"], " on mon0"), "#43A047"),
    ("IPv6", "Router Advertisement audit, DHCPv6", ("OK", C["good"], " 1 router, own"), "#43A047"),
    ("PATH", "ping, traceroute, path MTU", ("WARN", C["warn"], " loss 2 %"), "#1E88E5"),
    ("WATCH", "periodic ping or TCP, history graph", ("not running", C["muted"], ""), "#1E88E5"),
    ("RESULTS", "saved tests, export to USB", ("14 today", C["text"], ""), "#78909C"),
    ("DHCP / RA", "serve addresses on the test ports", ("OFF", C["muted"], ", ports silent"), "#FB8C00"),
    ("SYSTEM", "Wi-Fi, lock, power, service mode", ("Wi-Fi", C["text"], " Benswagin"), "#78909C"),
]


def draw_home(root, c):
    status_bar(c, "NETWORK ANALYZER")
    cols, rows = 4, 3
    tw = (W - 2 * M - G * (cols - 1)) // cols
    th = (H - M - TOP - G * (rows - 1)) // rows
    for i, (title, sub, (word, color, rest), accent) in enumerate(TILES):
        x = M + (i % cols) * (tw + G)
        y = TOP + (i // cols) * (th + G)
        _, f = card(root, x, y, tw, th, title, sub, C["panel"], accent, tsize=19, ssize=14)
        line = tk.Frame(f, bg=C["panel"])
        line.place(x=16, y=th - 32)
        tk.Label(line, text=word, font=font(16, True), fg=color, bg=C["panel"]).pack(side="left")
        tk.Label(line, text=rest, font=font(15), fg=C["muted"], bg=C["panel"]).pack(side="left")


METRICS = [("1 284", "packets/s"), ("12.6", "Mbit/s"), ("612 B", "avg size"), ("6", "hosts")]
SHARES = [("TCP", 71.2, 27348), ("UDP", 18.4, 7068), ("ICMP", 2.1, 806),
          ("ICMPv6", 6.3, 2419), ("ARP", 0.9, 346), ("other", 1.1, 425)]
TALKERS = [("fd00:1::2e0:4cff:fe68:223", 18.4), ("10.0.1.20", 6.1),
           ("fe80::2e0:4cff:fe68:201", 1.2), ("10.0.1.10", 0.8), ("192.168.100.1", 0.1)]
FEED = [
    ("12.911", "TCP", 1514, "fd00:1::2e0:4cff:fe68:223", "fd00:1::10", "5201"),
    ("12.910", "TCP", 66, "fd00:1::10", "fd00:1::2e0:4cff:fe68:223", "5201"),
    ("12.874", "ICMPv6", 118, "fe80::2e0:4cff:fe68:223", "ff02::1", "RA"),
    ("12.702", "UDP", 342, "10.0.1.20", "10.0.1.10", "bootps"),
    ("12.515", "ICMP", 98, "10.0.1.20", "10.0.1.10", "echo"),
    ("12.514", "ICMP", 98, "10.0.1.10", "10.0.1.20", "reply"),
    ("12.330", "ARP", 60, "10.0.1.20", "10.0.1.10", "who-has"),
    ("12.101", "UDP", 86, "fd00:1::2e0:4cff:fe68:223", "fd00:1::10", "domain"),
]


def draw_traffic(root, c):
    status_bar(c, "TRAFFIC")
    cw = (W - 2 * M - 4 * G) // 5
    y0 = TOP
    for i, (value, label) in enumerate(METRICS):
        x = M + i * (cw + G)
        c.create_rectangle(x, y0, x + cw, y0 + 52, fill=C["panel"], width=0)
        c.create_text(x + 12, y0 + 4, text=value, font=font(25, True), fill=C["text"], anchor="nw")
        c.create_text(x + 12, y0 + 33, text=label, font=font(14), fill=C["muted"], anchor="nw")
    x = M + 4 * (cw + G)
    c.create_rectangle(x, y0, W - M, y0 + 52, fill=C["panel"], width=0)
    c.create_text(x + 12, y0 + 4, text=DOT + " LIVE", font=font(23, True), fill=C["bad"], anchor="nw")
    c.create_text(x + 12, y0 + 33, text="mon0 " + MID + " 00:42", font=font(14), fill=C["muted"], anchor="nw")

    y1 = y0 + 60
    c.create_rectangle(M, y1, W - M, y1 + 60, fill=C["panel"], width=0)
    bx, bw = M + 10, W - 2 * M - 20
    for name, pct, _ in SHARES:
        w = max(2, round(bw * pct / 100))
        c.create_rectangle(bx, y1 + 7, bx + w, y1 + 19, fill=PROTO[name], width=0)
        bx += w
    iw = (W - 2 * M - 20) // len(SHARES)
    for i, (name, pct, count) in enumerate(SHARES):
        lx = M + 10 + i * iw
        c.create_rectangle(lx, y1 + 28, lx + 10, y1 + 38, fill=PROTO[name], width=0)
        c.create_text(lx + 15, y1 + 33, text=name, font=font(14, True), fill=C["text"], anchor="w")
        c.create_text(lx + iw - 14, y1 + 33, text="%.0f%%" % pct, font=font(14, True),
                      fill=C["text"], anchor="e")
        c.create_text(lx + 15, y1 + 50, text="{:,}".format(count).replace(",", " "), font=font(13),
                      fill=C["muted"], anchor="w")

    y2 = y1 + 68
    lw = 290
    c.create_rectangle(M, y2, M + lw, BOTTOM, fill=C["panel"], width=0)
    c.create_text(M + 10, y2 + 6, text="TOP TALKERS", font=font(14, True), fill=C["muted"], anchor="nw")
    c.create_text(M + lw - 10, y2 + 6, text="bytes", font=font(13), fill=C["dim"], anchor="ne")
    top = TALKERS[0][1]
    for i, (addr, mb) in enumerate(TALKERS):
        ry = y2 + 27 + i * 35
        c.create_text(M + 10, ry, text=short(addr), font=font(15), fill=C["text"], anchor="nw")
        c.create_text(M + lw - 10, ry, text="%.1f MB" % mb, font=font(15, True), fill=C["text"], anchor="ne")
        c.create_rectangle(M + 10, ry + 21, M + lw - 10, ry + 26, fill=C["line"], width=0)
        c.create_rectangle(M + 10, ry + 21, M + 10 + (lw - 20) * mb / top, ry + 26, fill=C["accent"], width=0)

    fx = M + lw + G
    c.create_rectangle(fx, y2, W - M, BOTTOM, fill=C["panel"], width=0)
    c.create_text(fx + 10, y2 + 6, text="PACKETS", font=font(14, True), fill=C["muted"], anchor="nw")
    c.create_text(W - M - 10, y2 + 6, text="filter: all traffic", font=font(13), fill=C["accent"], anchor="ne")
    for i, (t, proto, ln, src, dst, svc) in enumerate(FEED):
        ry = y2 + 29 + i * 22
        c.create_text(fx + 10, ry, text=t, font=font(13, family=MONO), fill=C["dim"], anchor="nw")
        c.create_text(fx + 66, ry, text=proto, font=font(13, True, MONO), fill=PROTO[proto], anchor="nw")
        c.create_text(fx + 162, ry, text=str(ln), font=font(13, family=MONO), fill=C["muted"], anchor="ne")
        c.create_text(fx + 174, ry, text="%s > %s" % (short(src), short(dst)), font=font(14),
                      fill=C["text"], anchor="nw")
        c.create_text(W - M - 10, ry, text=svc, font=font(13), fill=C["muted"], anchor="ne")

    port_bar(root, "mon0", ("PAUSE", 108, "#546E7A", "main"))


PAUSED = [
    (38412, "12.911", "TCP", 1514, "fd00:1::2e0:4cff:fe68:223", "fd00:1::10", "5201"),
    (38411, "12.910", "TCP", 66, "fd00:1::10", "fd00:1::2e0:4cff:fe68:223", "5201"),
    (38410, "12.874", "ICMPv6", 118, "fe80::2e0:4cff:fe68:223", "ff02::1", "Router Advertisement"),
    (38409, "12.702", "UDP", 342, "10.0.1.20", "10.0.1.10", "67 > 68  bootps"),
    (38408, "12.515", "ICMP", 98, "10.0.1.20", "10.0.1.10", "echo request"),
]


def draw_paused(root, c):
    status_bar(c, "PAUSED " + MID + " 1/40")
    lw = W - 2 * M - 92 - G
    rh = (BOTTOM - TOP - 4 * G) // 5
    for i, (num, t, proto, ln, src, dst, info) in enumerate(PAUSED):
        y = TOP + i * (rh + G)
        f = tk.Frame(root, bg=C["panel"])
        f.place(x=M, y=y, width=lw, height=rh)
        tap(f, "row")
        tk.Frame(f, bg=PROTO[proto]).place(x=0, y=0, width=6, relheight=1)
        tk.Label(f, text=proto, font=font(16, True), fg=PROTO[proto], bg=C["panel"]).place(x=16, y=6)
        tk.Label(f, text="#%d   %s   %d B   %s" % (num, t, ln, info), font=font(15), fg=C["muted"],
                 bg=C["panel"]).place(x=104, y=7)
        tk.Label(f, text="%s  %s  %s" % (src, ARR, dst), font=font(15, family=MONO), fg=C["text"],
                 bg=C["panel"]).place(x=16, y=32)
    px = W - M - 92
    h2 = (BOTTOM - TOP - G) // 2
    button(root, px, TOP, 92, h2, UP + "\nPAGE", C["panel2"], role="secondary", size=17)
    button(root, px, TOP + h2 + G, 92, h2, "PAGE\n" + DOWN, C["panel2"], role="secondary", size=17)
    port_bar(root, "mon0", ("RESUME", 108, "#2E7D32", "main"))


DETAIL = [
    ("Frame", "#38410   01:04:12.874   118 B   captured on mon0, incoming"),
    ("Ethernet", "00:e0:4c:68:02:23 > 33:33:00:00:00:01   type 0x86dd IPv6"),
    ("IPv6", "fe80::2e0:4cff:fe68:223 > ff02::1"),
    ("", "hop limit 255   payload 64 B   next header 58 ICMPv6"),
    ("ICMPv6", "type 134 Router Advertisement   code 0"),
    ("", "M=1 O=0   preference Medium   cur hop limit 64"),
    ("", "router lifetime 1800 s   reachable 0 ms   retrans 0 ms"),
    ("option", "prefix fd00:2::/64   L=1 A=1   valid 43200 s   pref 43200 s"),
    ("option", "MTU 1500"),
    ("option", "source link-layer 00:e0:4c:68:02:23"),
    ("Audit", "[OK]   another port of this device (snd0)"),
    ("", "[WARN] M and A both set: mixed DHCPv6 and SLAAC"),
]
LAYER = {"Frame": C["dim"], "Ethernet": C["accent"], "IPv6": PROTO["ICMPv6"], "ICMPv6": PROTO["ICMPv6"],
         "option": C["muted"], "Audit": C["good"]}


def draw_detail(root, c):
    status_bar(c, "PACKET #38410")
    pw = W - 2 * M - 92 - G
    c.create_rectangle(M, TOP, M + pw, BOTTOM, fill=C["panel"], width=0)
    for i, (layer, text) in enumerate(DETAIL):
        y = TOP + 10 + i * 27
        if layer:
            if i:
                c.create_line(M + 8, y - 5, M + pw - 8, y - 5, fill=C["line"])
            c.create_text(M + 12, y, text=layer, font=font(15, True), fill=LAYER[layer], anchor="nw")
        color = C["warn"] if "[WARN]" in text else C["good"] if "[OK]" in text else C["text"]
        c.create_text(M + 100, y, text=text, font=font(14, family=MONO), fill=color, anchor="nw")
    px = W - M - 92
    h2 = (BOTTOM - TOP - G) // 2
    button(root, px, TOP, 92, h2, UP, C["panel2"], role="secondary", size=22)
    button(root, px, TOP + h2 + G, 92, h2, DOWN, C["panel2"], role="secondary", size=22)
    bottom_bar(root, [
        (LEFT + "  PREV", 150, C["panel2"], "main"), ("NEXT  " + RIGHT, 150, C["panel2"], "main"),
        ("FILTER\nTHIS HOST", 180, "#00838F", "main"),
    ])


FILTERS = [
    ("ALL", "no filter"), ("TCP", "tcp"), ("UDP", "udp"),
    ("ICMP", "icmp or icmp6"), ("ARP", "arp"), ("DHCP", "udp port 67 or 68 or 546 or 547"),
    ("ND / RA", "icmp6 types 133 to 137"), ("DNS", "port 53"), ("HOST", "pick from top talkers"),
]


def draw_filter(root, c):
    status_bar(c, "TRAFFIC " + MID + " FILTER")
    c.create_text(M, TOP + 2, text="The filter runs in the kernel as BPF: packets that do not match never reach the program.",
                  font=font(14), fill=C["muted"], anchor="nw")
    cols = 3
    bw = (W - 2 * M - G * (cols - 1)) // cols
    bh = (BOTTOM - TOP - 26 - 2 * G) // 3
    for i, (name, bpf) in enumerate(FILTERS):
        x = M + (i % cols) * (bw + G)
        y = TOP + 26 + (i // cols) * (bh + G)
        active = name == "ALL"
        card(root, x, y, bw, bh, name, bpf, C["panel2"] if active else C["panel"],
             border=C["accent"] if active else None, tsize=22, ssize=14)
    c.create_text(M, BTN_Y + BTN_H // 2, text="now: ALL, no filter", font=font(17, True), fill=C["muted"], anchor="w")
    back(root)


def check():
    rects = []
    for w in TAPS:
        rects.append((w.role, w.winfo_rootx(), w.winfo_rooty(), w.winfo_width(), w.winfo_height(),
                      w.cget("text").replace("\n", " ") if isinstance(w, tk.Button) else "card"))
    bad = []
    for role, x, y, w, h, name in rects:
        need = 80 if role == "main" else 60
        if (role == "main" and (w < need or h < need)) or (role != "main" and min(w, h) < need):
            bad.append("U1 %s %dx%d < %d (%s)" % (name, w, h, need, role))
        if x < M or y < M or x + w > W - M or y + h > H - M:
            bad.append("U2 edge %s at %d,%d %dx%d" % (name, x, y, w, h))
    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            dx = max(b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]))
            dy = max(b[2] - (a[2] + a[4]), a[2] - (b[2] + b[4]))
            if max(dx, dy) < G:
                bad.append("U2 gap %d px: %s / %s" % (max(dx, dy), a[5], b[5]))
    print("tappable %d, violations %d" % (len(rects), len(bad)))
    for line in bad:
        print("  " + line)


def main():
    name = sys.argv[1]
    root, c = screen()
    {"home": draw_home, "traffic": draw_traffic, "paused": draw_paused,
     "detail": draw_detail, "filter": draw_filter}[name](root, c)

    def shot():
        root.update_idletasks()
        check()
        subprocess.run(["scrot", "-o", "/tmp/mock_%s.png" % name])
        root.destroy()

    root.after(1500, shot)
    root.mainloop()


if __name__ == "__main__":
    main()
