import subprocess
import sys
import tkinter as tk

sys.path.insert(0, "/home/muk0015/diploma_project")
from ui_kit import BOTTOM, BTN_H, BTN_Y, C, G, M, TOP, W, H, StatusBar, VERDICT_H, button, font

# Fake data for the screenshot only: documentation and private ranges, not a real network
STATE = sys.argv[1] if len(sys.argv) > 1 else "done"
DONE = [("LINK", "PASS", "1000 Mb/s full duplex, autoneg on", "partner 1000F 100F 100H 10F 10H"),
        ("DHCPv4", "WARN", "2 servers answered: 10.20.30.1, 10.20.30.250",
         "took 10.20.30.57/24 from 10.20.30.1 in 6 ms, lease 1 h, returned"),
        ("IPv6", "PASS", "RA from fe80::1, prefix 2001:db8:141::/64, A=1",
         "SLAAC address 2001:db8:141:0:2e0:4cff:fe68:201"),
        ("GATEWAY", "PASS", "10.20.30.1: 3/3, 0.8 ms", "fe80::1: 3/3, 0.9 ms"),
        ("DNS", "PASS", "www.vsb.cz in 9 ms via 10.20.30.53", "A 192.0.2.10, AAAA 2001:db8::10"),
        ("TARGETS", "PASS", "www.vsb.cz port 443: connected in 12 ms", "")]
RUN = DONE[:3] + [("GATEWAY", "RUNNING", "ping 10.20.30.1 " + chr(0x2026), ""),
                  ("DNS", "WAIT", "", ""), ("TARGETS", "WAIT", "", "")]
COLORS = {"PASS": "good", "WARN": "warn", "FAIL": "bad", "SKIP": "dim", "RUNNING": "accent", "WAIT": "dim"}


def main():
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("%dx%d+0+0" % (W, H))
    root.attributes("-topmost", True)
    root.config(cursor="none", bg=C["bg"])
    bar = StatusBar(root, "AUTOTEST")
    bar.draw({"ports": {"mon0": {"present": True, "carrier": True, "speed": 1000},
                        "snd0": {"present": True, "carrier": False}},
              "dhcp": False, "ssid": "iPhone", "time": "16:24", "battery": (90, C["good"])})
    v = tk.Canvas(root, width=W - 2 * M, height=VERDICT_H, bg=C["panel"], highlightthickness=0)
    v.place(x=M, y=TOP)
    if STATE == "done":
        word, color, text = "WARN", "warn", "2 DHCP servers on mon0; 6 steps in 9.8 s"
        rows = DONE
    else:
        word, color, text = "RUNNING", "accent", "autotest on mon0, step 4 of 6, 5 s"
        rows = RUN
    v.create_text(12, VERDICT_H // 2, text=word, font=font(22, True), fill=C[color], anchor="w")
    v.create_text(150, VERDICT_H // 2, text=text, font=font(19), fill=C["text"], anchor="w")
    y = TOP + VERDICT_H + G
    h = BOTTOM - y
    c = tk.Canvas(root, width=W - 2 * M, height=h, bg=C["panel"], highlightthickness=0)
    c.place(x=M, y=y)
    rh = h // len(rows)
    for i, (name, res, line1, line2) in enumerate(rows):
        yy = i * rh
        if i:
            c.create_line(10, yy, W - 2 * M - 10, yy, fill=C["line"])
        c.create_text(14, yy + 8, text=name, font=font(17, True), fill=C["text"] if res != "WAIT" else C["dim"],
                      anchor="nw")
        c.create_text(120, yy + 8, text=res if res != "WAIT" else "waiting", font=font(17, True),
                      fill=C[COLORS[res]], anchor="nw")
        c.create_text(232, yy + 7, text=line1, font=font(16), fill=C["text"], anchor="nw")
        c.create_text(232, yy + 27, text=line2, font=font(14), fill=C["muted"], anchor="nw")
    x = M
    for name in ("mon0", "snd0"):
        button(root, x, BTN_Y, 92, BTN_H, "%s\n%s" % ("MON" if name == "mon0" else "SND", name),
               C["sel"] if name == "mon0" else C["panel2"], None, "secondary", 17)
        x += 92 + G
    free = W - M - 110 - G - x - G
    first = free * 3 // 5
    if STATE == "done":
        button(root, x, BTN_Y, first, BTN_H, "START", C["go"], None, "main", 17)
    else:
        button(root, x, BTN_Y, first, BTN_H, "STOP", C["stop"], None, "main", 17)
    button(root, x + first + G, BTN_Y, free - first, BTN_H, "DETAILS", C["panel2"], None, "secondary", 17)
    button(root, W - M - 110, BTN_Y, 110, BTN_H, "BACK", C["back"], None, "secondary", 17)
    root.after(1500, lambda: (subprocess.run(["scrot", "-o", "/tmp/mock_autotest_%s.png" % STATE]), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
