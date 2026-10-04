import subprocess
import sys
import tkinter as tk

sys.path.insert(0, "/home/muk0015/diploma_project")
from ui_kit import BOTTOM, BTN_H, BTN_Y, C, G, M, TOP, W, H, StatusBar, VERDICT_H, button, font

# Fake state for the screenshot: mon0 plugged into a lab switch that sends LLDP
STATE = sys.argv[1] if len(sys.argv) > 1 else "found"

LINK = [("Link", "up, 1000 Mb/s, full duplex", "good"),
        ("Autoneg", "on, both sides", "text"),
        ("Partner", "1000F 100F 100H 10F 10H", "text"),
        ("This port", "1000F 100F 100H 10F 10H", "text"),
        ("Link drops", "0 since boot", "text"),
        ("Errors", "0 new since last check", "text"),
        ("Adapter", "r8152, rtl8153a-2", "muted"),
        ("MAC", "00:e0:4c:68:02:01", "muted")]

SWITCH = [("Name", "MikroTik-EB215", "text"),
          ("Port", "ether5 (desk 3)", "text"),
          ("VLAN", "10", "text"),
          ("Mgmt IP", "192.168.88.1", "text"),
          ("Model", "RouterOS 7.15 CRS326", "muted"),
          ("Chassis", "4c:5e:0c:12:34:56", "muted"),
          ("TTL", "120 s", "muted"),
          ("Also", "STP, root 4c:5e:0c:12:34:56", "muted")]


def panel(root, x, y, w, h, title, rows, kx=110):
    c = tk.Canvas(root, width=w, height=h, bg=C["panel"], highlightthickness=0)
    c.place(x=x, y=y)
    c.create_text(14, 8, text=title, font=font(14, True), fill=C["muted"], anchor="nw")
    for i, (k, v, color) in enumerate(rows):
        yy = 36 + i * 30
        c.create_text(14, yy, text=k, font=font(16), fill=C["muted"], anchor="nw")
        c.create_text(kx, yy, text=v, font=font(16, color != "muted"), fill=C[color], anchor="nw")
    return c


def main():
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("%dx%d+0+0" % (W, H))
    root.attributes("-topmost", True)
    root.config(cursor="none", bg=C["bg"])
    bar = StatusBar(root, "PORT")
    bar.draw({"ports": {"mon0": {"present": True, "carrier": True, "speed": 1000},
                        "snd0": {"present": True, "carrier": False}},
              "dhcp": False, "ssid": "iPhone", "time": "16:20", "battery": (91, C["good"])})
    v = tk.Canvas(root, width=W - 2 * M, height=VERDICT_H, bg=C["panel"], highlightthickness=0)
    v.place(x=M, y=TOP)
    if STATE == "found":
        word, color, text = "PASS", "good", "1000 full on mon0, switch MikroTik-EB215 port ether5"
    else:
        word, color, text = "RUNNING", "accent", "listening for LLDP and CDP on mon0, 23 s of 65"
    v.create_text(12, VERDICT_H // 2, text=word, font=font(22, True), fill=C[color], anchor="w")
    v.create_text(150, VERDICT_H // 2, text=text, font=font(19), fill=C["text"], anchor="w")
    y = TOP + VERDICT_H + G
    h = BOTTOM - y
    pw = (W - 2 * M - G) // 2
    panel(root, M, y, pw, h, "LINK  (read from the adapter)", LINK)
    if STATE == "found":
        panel(root, M + pw + G, y, W - 2 * M - pw - G, h, "SWITCH  LLDP, heard 14 s ago", SWITCH, kx=100)
    else:
        c = panel(root, M + pw + G, y, W - 2 * M - pw - G, h, "SWITCH  listening, sending nothing", [], kx=100)
        lines = [("LLDP comes every 30 s,", "text"), ("CDP every 60 s.", "text"), ("", "text"),
                 ("Heard so far:", "muted"), ("STP from 4c:5e:0c:12:34:56", "muted"),
                 ("no LLDP or CDP yet", "muted")]
        for i, (t, col) in enumerate(lines):
            c.create_text(14, 36 + i * 30, text=t, font=font(16), fill=C[col], anchor="nw")
        c.create_rectangle(14, h - 20, 14 + int((W - 2 * M - pw - G - 28) * 23 / 65), h - 12,
                           fill=C["accent"], width=0)
    x = M
    for name in ("mon0", "snd0"):
        button(root, x, BTN_Y, 92, BTN_H, "%s\n%s" % ("MON" if name == "mon0" else "SND", name),
               C["sel"] if name == "mon0" else C["panel2"], None, "secondary", 17)
        x += 92 + G
    free = W - M - 110 - G - x - G
    button(root, x, BTN_Y, free // 2, BTN_H, "CHECK", "#2E7D32", None, "main", 17)
    if STATE == "found":
        button(root, x + free // 2 + G, BTN_Y, free - free // 2, BTN_H, "LISTEN", "#00838F", None, "main", 17)
    else:
        button(root, x + free // 2 + G, BTN_Y, free - free // 2, BTN_H, "STOP", C["stop"], None, "main", 17)
    button(root, W - M - 110, BTN_Y, 110, BTN_H, "BACK", C["back"], None, "secondary", 17)
    root.after(1500, lambda: (subprocess.run(["scrot", "-o", "/tmp/mock_port_%s.png" % STATE]), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
