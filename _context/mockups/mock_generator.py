import subprocess
import sys
import tkinter as tk

sys.path.insert(0, "/home/muk0015/diploma_project")
from ui_kit import BOTTOM, BTN_H, BTN_Y, C, G, M, TOP, W, H, StatusBar, VERDICT_H, button, font

# Fake state for the screenshot: 1000 ICMPv6 echo at 100/s sent from snd0, counted on mon0
PROTOS = ["ICMP", "ICMPv6", "UDP", "TCP SYN", "ARP", "RS"]
PARAMS = [("COUNT", "1000"), ("RATE", "100 /s"), ("SIZE", "512 B"), ("TO", "mon0 auto")]


def main():
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("%dx%d+0+0" % (W, H))
    root.attributes("-topmost", True)
    root.config(cursor="none", bg=C["bg"])
    bar = StatusBar(root, "GENERATOR")
    bar.draw({"ports": {"mon0": {"present": True, "carrier": True, "speed": 1000},
                        "snd0": {"present": True, "carrier": True, "speed": 1000}},
              "dhcp": True, "ssid": "Benswagin", "time": "17:55", "battery": (84, C["good"])})
    v = tk.Canvas(root, width=W - 2 * M, height=VERDICT_H, bg=C["panel"], highlightthickness=0)
    v.place(x=M, y=TOP)
    v.create_text(12, VERDICT_H // 2, text="PASS", font=font(22, True), fill=C["good"], anchor="w")
    v.create_text(150, VERDICT_H // 2, text="1000 sent from snd0, 1000 received on mon0, 0 lost",
                  font=font(19), fill=C["text"], anchor="w")
    y = TOP + VERDICT_H + G
    bw = (W - 2 * M - 5 * G) // 6
    for i, p in enumerate(PROTOS):
        button(root, M + i * (bw + G), y, bw, 64, p, C["sel"] if p == "ICMPv6" else C["panel2"], None,
               "secondary", 17)
    y += 64 + G
    pw = (W - 2 * M - 3 * G) // 4
    for i, (k, val) in enumerate(PARAMS):
        button(root, M + i * (pw + G), y, pw, 64, "%s\n%s" % (k, val), C["panel"], None, "secondary", 16)
    y += 64 + G
    c = tk.Canvas(root, width=W - 2 * M, height=BOTTOM - y, bg=C["panel"], highlightthickness=0)
    c.place(x=M, y=y)
    h = BOTTOM - y
    half = (W - 2 * M) // 2
    for i, (label, value, sub) in enumerate((("SENT on snd0", "1 000", "100 pkt/s, 10.0 s"),
                                             ("RECEIVED on mon0", "1 000", "0 lost, counted in its own namespace"))):
        x = 14 + i * half
        c.create_text(x, 8, text=label, font=font(14, True), fill=C["muted"], anchor="nw")
        c.create_text(x, 28, text=value, font=font(30, True), fill=C["text"], anchor="nw")
        c.create_text(x, 66, text=sub, font=font(14), fill=C["muted"], anchor="nw")
    c.create_rectangle(14, h - 14, W - 2 * M - 14, h - 8, fill=C["line"], width=0)
    c.create_rectangle(14, h - 14, W - 2 * M - 14, h - 8, fill=C["good"], width=0)
    x = M
    for name in ("mon0", "snd0"):
        button(root, x, BTN_Y, 92, BTN_H, "%s\n%s" % ("MON" if name == "mon0" else "SND", name),
               C["sel"] if name == "snd0" else C["panel2"], None, "secondary", 17)
        x += 92 + G
    button(root, x, BTN_Y, W - M - 110 - G - x, BTN_H, "SEND", C["go"], None, "main", 17)
    button(root, W - M - 110, BTN_Y, 110, BTN_H, "BACK", C["back"], None, "secondary", 17)
    root.after(1500, lambda: (subprocess.run(["scrot", "-o", "/tmp/mock_generator.png"]), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
