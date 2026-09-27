import subprocess
import sys
import tkinter as tk

sys.path.insert(0, "/home/muk0015/diploma_project")
from ui_kit import BOTTOM, BTN_H, BTN_Y, C, G, M, TOP, W, H, StatusBar, VERDICT_H, button, font, RIGHT

# Fake data for the screenshots; speeds are the ones measured against the laptop on 27.09.2026
STATUS = {"ports": {"mon0": {"present": True, "carrier": True, "speed": 1000},
                    "snd0": {"present": True, "carrier": True, "speed": 1000}},
          "dhcp": True, "ssid": "Benswagin", "time": "20:15", "battery": (80, C["good"])}
SWEEP = [(64, 18, "11.9", "23 210", "4.1 %", "0.21"), (128, 82, "22.6", "22 070", "0", "0.19"),
         (256, 210, "44.8", "21 880", "0", "0.12"), (512, 466, "88.2", "21 530", "0", "0.08"),
         (1024, 978, "172.4", "21 040", "0", "0.06"), (1280, 1234, "214.0", "20 900", "0", "0.05"),
         (1518, 1472, "264.6", "21 790", "0", "0.05")]


def base(root, title, verdict, text):
    StatusBar(root, title).draw(STATUS)
    v = tk.Canvas(root, width=W - 2 * M, height=VERDICT_H, bg=C["panel"], highlightthickness=0)
    v.place(x=M, y=TOP)
    color = {"PASS": "good", "RUNNING": "accent"}.get(verdict, "text")
    v.create_text(12, VERDICT_H // 2, text=verdict, font=font(22, True), fill=C[color], anchor="w")
    v.create_text(150, VERDICT_H // 2, text=text, font=font(19), fill=C["text"], anchor="w")


def bottom(root, items):
    x = M
    for name in ("mon0", "snd0"):
        button(root, x, BTN_Y, 92, BTN_H, "%s\n%s" % ("MON" if name == "mon0" else "SND", name),
               C["sel"] if name == "mon0" else C["panel2"], None, "secondary", 17)
        x += 92 + G
    free = W - M - 110 - G - x - G * (len(items) - 1)
    for text, color in items:
        w = free // len(items)
        button(root, x, BTN_Y, w, BTN_H, text, color, None, "main", 17)
        x += w + G
    button(root, W - M - 110, BTN_Y, 110, BTN_H, "BACK", C["back"], None, "secondary", 17)


def selectors(root, y, server=False):
    bw = (W - 2 * M - 3 * G) // 4
    for i, (t, on) in enumerate((("TCP", False), ("UDP", True), ("IPv4", True), ("IPv6", False))):
        button(root, M + i * (bw + G), y, bw, 64, t, C["sel"] if on else C["panel2"], None, "secondary", 17)
    y += 64 + G
    params = [("RATE", "100 Mbit/s"), ("TIME", "10 s"), ("DIRECTION", "device %s host" % RIGHT), ("TO", "auto")]
    for i, (k, val) in enumerate(params):
        button(root, M + i * (bw + G), y, bw, 64, "%s\n%s" % (k, val), C["panel"], None, "secondary", 16)
    return y + 64 + G


def speed(root):
    base(root, "SPEED", "PASS", "100.0 Mbit/s UDP v4, 0 % lost, jitter 0.17 ms")
    y = selectors(root, TOP + VERDICT_H + G)
    c = tk.Canvas(root, width=W - 2 * M, height=BOTTOM - y, bg=C["panel"], highlightthickness=0)
    c.place(x=M, y=y)
    cw = (W - 2 * M - 28) // 4
    for i, (label, value, unit) in enumerate((("THROUGHPUT", "100.0", "Mbit/s"), ("PACKETS", "8 634", "pkt/s"),
                                              ("LOST", "0", "0.00 %"), ("JITTER", "0.17", "ms"))):
        x = 14 + i * cw
        c.create_text(x, 8, text=label, font=font(14, True), fill=C["muted"], anchor="nw")
        c.create_text(x, 28, text=value, font=font(30, True), fill=C["text"], anchor="nw")
        c.create_text(x, 66, text=unit, font=font(14), fill=C["muted"], anchor="nw")
    c.create_text(14, 100, text="to DESKTOP-87OV3HU 10.0.1.20 (DHCP lease)   CPU 31 %%   SoC 49 %s 51 C, "
                               "no throttling" % RIGHT, font=font(14), fill=C["muted"], anchor="nw")
    bottom(root, [("START", C["go"]), ("SWEEP", C["action"]), ("SERVER", "#546E7A")])


def sweep(root):
    base(root, "SPEED " + chr(0x00B7) + " SWEEP", "PASS", "UDP v4, 7 frame sizes in 1 min 24 s")
    y = TOP + VERDICT_H + G
    c = tk.Canvas(root, width=W - 2 * M, height=BOTTOM - y, bg=C["panel"], highlightthickness=0)
    c.place(x=M, y=y)
    cols = [(14, "FRAME B"), (130, "UDP DATA"), (270, "Mbit/s"), (400, "pkt/s"), (540, "LOST"), (650, "JITTER ms")]
    for x, t in cols:
        c.create_text(x, 10, text=t, font=font(14, True), fill=C["muted"], anchor="nw")
    for r, row in enumerate(SWEEP):
        yy = 38 + r * 31
        for (x, _), val in zip(cols, row):
            color = C["warn"] if str(val).endswith("%") else C["text"]
            c.create_text(x, yy, text=str(val), font=font(19, family="DejaVu Sans Mono"), fill=color, anchor="nw")
    c.create_text(14, 38 + 7 * 31 + 6, text="offered: as fast as possible, 10 s per size; saved as CSV and JSON",
                  font=font(14), fill=C["muted"], anchor="nw")
    bottom(root, [("SWEEP v4", C["action"]), ("SWEEP v6", "#00695C")])


def server(root):
    base(root, "SPEED", "RUNNING", "server on mon0, 2 min 10 s, 2 tests served")
    y = selectors(root, TOP + VERDICT_H + G)
    c = tk.Canvas(root, width=W - 2 * M, height=BOTTOM - y, bg=C["panel"], highlightthickness=0)
    c.place(x=M, y=y)
    c.create_text(14, 8, text="Waiting for iperf3 clients on mon0. On the other computer run:", font=font(16),
                  fill=C["muted"], anchor="nw")
    c.create_text(14, 34, text="iperf3 -c 10.0.1.10      iperf3 -c fd00:1::10", font=font(22, True,
                  "DejaVu Sans Mono"), fill=C["text"], anchor="nw")
    c.create_text(14, 76, text="last: 10.0.1.20  TCP  246.1 Mbit/s  10 s", font=font(16), fill=C["text"],
                  anchor="nw")
    c.create_text(14, 102, text="before: fd00:1::20  UDP  100.0 Mbit/s  0 % lost", font=font(16),
                  fill=C["muted"], anchor="nw")
    bottom(root, [("START", C["dim"]), ("SWEEP", C["dim"]), ("STOP", C["stop"])])


def main():
    which = sys.argv[1]
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("%dx%d+0+0" % (W, H))
    root.attributes("-topmost", True)
    root.config(cursor="none", bg=C["bg"])
    {"speed": speed, "sweep": sweep, "server": server}[which](root)
    root.after(1500, lambda: (subprocess.run(["scrot", "-o", "/tmp/mock_%s.png" % which]), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
