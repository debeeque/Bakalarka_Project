import re
import subprocess
import threading
import tkinter as tk

FONT = 'Arial'
BG = "#ECEFF1"


def nmcli(*args, timeout=45):
    try:
        r = subprocess.run(["sudo", "nmcli", *args], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 1, "timeout"
    return r.returncode, (r.stdout + r.stderr).strip()


# nmcli terse output separates fields with ':' and escapes ':' inside values
def split_terse(line):
    return [p.replace("\\:", ":").replace("\\\\", "\\") for p in re.split(r"(?<!\\):", line)]


def wifi_status():
    ssid = ip = None
    try:
        out = subprocess.run(["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi", "list", "--rescan", "no"],
                             capture_output=True, text=True, timeout=5).stdout
        for line in out.splitlines():
            f = split_terse(line)
            if len(f) >= 2 and f[0] == "yes":
                ssid = f[1]
        out = subprocess.run(["nmcli", "-g", "IP4.ADDRESS", "dev", "show", "wlan0"],
                             capture_output=True, text=True, timeout=5).stdout
        ip = out.split("/")[0].strip() or None
    except (OSError, subprocess.SubprocessError):
        pass
    return ssid, ip


def scan():
    code, out = nmcli("-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "dev", "wifi", "list", "--rescan", "yes")
    if code != 0:
        return None, out
    nets = {}
    for line in out.splitlines():
        f = split_terse(line)
        if len(f) < 4 or not f[1]:
            continue
        net = {"ssid": f[1], "signal": int(f[2] or 0), "secure": f[3] not in ("", "--"), "inuse": f[0] == "*"}
        old = nets.get(net["ssid"])
        if old:
            net["inuse"] = net["inuse"] or old["inuse"]
            net["signal"] = max(net["signal"], old["signal"])
        nets[net["ssid"]] = net
    return sorted(nets.values(), key=lambda n: (not n["inuse"], -n["signal"])), ""


def saved_profiles():
    code, out = nmcli("-t", "-f", "NAME,TYPE", "con", "show")
    profiles = {}
    for line in out.splitlines() if code == 0 else []:
        f = split_terse(line)
        if len(f) >= 2 and f[1] == "802-11-wireless":
            c, ssid = nmcli("-g", "802-11-wireless.ssid", "con", "show", f[0])
            if c == 0 and ssid:
                profiles[split_terse(ssid)[0]] = f[0]
    return profiles


class OnScreenKeyboard(tk.Frame):
    LAYOUTS = {
        "abc": ["1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm"],
        "sym": ["1234567890", "!@#$%^&*()", "-_=+[]{}\\|~", ";:'\",.<>/?`"],
    }
    KEY_W, KEY_H = 66, 50

    def __init__(self, parent, entry):
        super().__init__(parent, bg=BG)
        self.entry = entry
        self.layout = "abc"
        self.caps = False
        self.build()

    def key(self, row, text, width, cmd, bg="#FAFAFA"):
        f = tk.Frame(row, width=width, height=self.KEY_H)
        f.pack_propagate(False)
        f.pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(f, text=text, font=(FONT, 14, 'bold'), bg=bg, command=cmd).pack(fill=tk.BOTH, expand=True)

    def build(self):
        for w in self.winfo_children():
            w.destroy()
        for chars in self.LAYOUTS[self.layout]:
            row = tk.Frame(self, bg=BG)
            row.pack()
            for ch in chars:
                ch = ch.upper() if self.caps else ch
                self.key(row, ch, self.KEY_W, lambda c=ch: self.entry.insert(tk.END, c))
        row = tk.Frame(self, bg=BG)
        row.pack()
        self.key(row, "SHIFT", 110, self.toggle_caps, "#90CAF9" if self.caps else "#CFD8DC")
        self.key(row, "?123" if self.layout == "abc" else "abc", 110, self.toggle_layout, "#CFD8DC")
        self.key(row, "SPACE", 300, lambda: self.entry.insert(tk.END, " "))
        self.key(row, "DEL", 130, self.backspace, "#FFCDD2")

    def toggle_caps(self):
        self.caps = not self.caps
        self.build()

    def toggle_layout(self):
        self.layout = "sym" if self.layout == "abc" else "abc"
        self.build()

    def backspace(self):
        text = self.entry.get()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text[:-1])


class NetworkList(tk.Frame):
    ROW_H = 54
    ROW_BG, SEL_BG = "white", "#BBDEFB"

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.canvas = tk.Canvas(self, bg=self.ROW_BG, highlightthickness=0)
        bar = tk.Scrollbar(self, command=self.canvas.yview, width=30)
        self.canvas.config(yscrollcommand=bar.set)
        bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.inner = tk.Frame(self.canvas, bg=self.ROW_BG)
        item = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.config(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(item, width=e.width))
        self.rows, self.selected = [], None

    def set(self, nets, profiles):
        for w in self.inner.winfo_children():
            w.destroy()
        self.rows, self.selected = [], None
        for i, n in enumerate(nets):
            self.rows.append(self.make_row(i, n, n["ssid"] in profiles))
        self.canvas.yview_moveto(0)

    def make_row(self, i, net, saved):
        row = tk.Frame(self.inner, bg=self.ROW_BG, height=self.ROW_H)
        row.pack(fill=tk.X)
        row.pack_propagate(False)
        tk.Frame(self.inner, bg="#CFD8DC", height=1).pack(fill=tk.X)

        bars = tk.Canvas(row, width=36, height=30, bg=self.ROW_BG, highlightthickness=0)
        level = min(4, (net["signal"] + 24) // 25)
        for b in range(4):
            h = 8 + b * 7
            bars.create_rectangle(b * 9, 30 - h, b * 9 + 6, 30, width=0,
                                  fill="#0277BD" if b < level else "#CFD8DC")
        bars.pack(side=tk.RIGHT, padx=(4, 12))
        pct = tk.Label(row, text=f"{net['signal']}%", font=(FONT, 12), fg="#546E7A", bg=self.ROW_BG, width=4, anchor="e")
        pct.pack(side=tk.RIGHT)

        text = tk.Frame(row, bg=self.ROW_BG)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12)
        name = tk.Label(text, text=net["ssid"], font=(FONT, 15, 'bold'), anchor="w", bg=self.ROW_BG,
                        fg="#2E7D32" if net["inuse"] else "black")
        name.pack(fill=tk.X, pady=(5, 0))
        tags = (["connected"] if net["inuse"] else []) + (["saved"] if saved else []) + \
               ["secured" if net["secure"] else "open"]
        info = tk.Label(text, text="  \u00b7  ".join(tags), font=(FONT, 10), fg="#78909C", anchor="w", bg=self.ROW_BG)
        info.pack(fill=tk.X)

        widgets = (row, bars, pct, text, name, info)
        for w in widgets:
            w.bind("<Button-1>", lambda e, k=i: self.select(k))
        return widgets

    def select(self, i):
        self.selected = i
        for k, widgets in enumerate(self.rows):
            for w in widgets:
                w.config(bg=self.SEL_BG if k == i else self.ROW_BG)


class WifiDialog:
    def __init__(self, root, log=print, on_close=None):
        self.root, self.log, self.on_close = root, log, on_close
        self.nets, self.profiles = [], {}

        self.win = tk.Toplevel(root)
        self.win.title("Wi-Fi")
        self.win.geometry("800x480+0+0")
        self.win.attributes('-topmost', True)
        self.win.configure(bg=BG, cursor="none")

        top = tk.Frame(self.win, bg=BG)
        top.pack(fill=tk.X, padx=8, pady=6)
        self.status = tk.Label(top, text="Wi-Fi", font=(FONT, 13, 'bold'), bg=BG, anchor="w")
        self.status.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(top, text="CLOSE", font=(FONT, 11, 'bold'), bg="#f44336", fg="white",
                  height=2, width=9, command=self.close).pack(side=tk.RIGHT)

        self.page = tk.Frame(self.win, bg=BG)
        self.page.pack(fill=tk.BOTH, expand=True)
        self.show_list()
        self.rescan()

    # Worker threads schedule through root: the dialog may be closed meanwhile
    def ui(self, fn, *args):
        self.root.after(0, lambda: fn(*args) if self.win.winfo_exists() else None)

    def set_status(self, text, color="black"):
        self.status.config(text=text, fg=color)

    def clear_page(self):
        for w in self.page.winfo_children():
            w.destroy()

    def show_list(self):
        self.clear_page()
        self.netlist = NetworkList(self.page)
        self.netlist.pack(fill=tk.BOTH, expand=True, padx=8)
        self.netlist.set(self.nets, self.profiles)

        btns = tk.Frame(self.page, bg=BG)
        btns.pack(fill=tk.X, padx=8, pady=8)
        cfg = {'font': (FONT, 12, 'bold'), 'height': 2, 'width': 14, 'fg': "white"}
        tk.Button(btns, text="RESCAN", bg="#607D8B", command=self.rescan, **cfg).pack(side=tk.LEFT, padx=4)
        tk.Button(btns, text="CONNECT", bg="#4CAF50", command=self.connect_selected, **cfg).pack(side=tk.LEFT, padx=4)
        tk.Button(btns, text="DISCONNECT", bg="#E64A19", command=self.disconnect, **cfg).pack(side=tk.RIGHT, padx=4)

    def rescan(self):
        self.set_status("Scanning...", "orange")

        def task():
            profiles = saved_profiles()
            nets, err = scan()
            self.ui(self.scan_done, profiles, nets, err)

        threading.Thread(target=task, daemon=True).start()

    def scan_done(self, profiles, nets, err):
        if nets is None:
            self.set_status(f"Scan failed: {err[:60]}", "red")
            return
        self.profiles, self.nets = profiles, nets
        if hasattr(self, 'netlist') and self.netlist.winfo_exists():
            self.netlist.set(nets, profiles)
        self.show_current()

    def show_current(self):
        ssid, ip = wifi_status()
        if ssid:
            self.set_status(f"Connected: {ssid}  ({ip or 'no IP'})", "darkgreen")
        else:
            self.set_status("Not connected", "black")

    def connect_selected(self):
        if self.netlist.selected is None:
            self.set_status("Select a network first", "red")
            return
        net = self.nets[self.netlist.selected]
        if net["ssid"] in self.profiles:
            self.run_connect(["con", "up", "id", self.profiles[net["ssid"]]], net, ask_on_fail=True)
        elif not net["secure"]:
            self.run_connect(["dev", "wifi", "connect", net["ssid"], "ifname", "wlan0"], net)
        else:
            self.show_password(net)

    def show_password(self, net):
        self.clear_page()
        row = tk.Frame(self.page, bg=BG)
        row.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(row, text=f"Password for {net['ssid']}:", font=(FONT, 12), bg=BG).pack(side=tk.LEFT)
        entry = tk.Entry(row, font=(FONT, 16), width=18, show="*")
        entry.pack(side=tk.LEFT, padx=6)
        show = tk.Button(row, text="SHOW", font=(FONT, 10, 'bold'), height=2, width=6)
        show.config(command=lambda: (entry.config(show="" if entry.cget("show") else "*"),
                                     show.config(text="HIDE" if not entry.cget("show") else "SHOW")))
        show.pack(side=tk.LEFT, padx=2)
        tk.Button(row, text="BACK", font=(FONT, 10, 'bold'), height=2, width=6,
                  command=self.show_list).pack(side=tk.RIGHT, padx=2)
        tk.Button(row, text="CONNECT", font=(FONT, 10, 'bold'), bg="#4CAF50", fg="white", height=2, width=9,
                  command=lambda: self.run_connect(["dev", "wifi", "connect", net["ssid"], "password",
                                                    entry.get(), "ifname", "wlan0"], net)).pack(side=tk.RIGHT, padx=2)
        OnScreenKeyboard(self.page, entry).pack(pady=4)

    def run_connect(self, args, net, ask_on_fail=False):
        self.set_status(f"Connecting to {net['ssid']}...", "orange")

        def task():
            code, out = nmcli("-w", "30", *args)
            self.ui(self.connect_done, code, out, net, ask_on_fail)

        threading.Thread(target=task, daemon=True).start()

    def connect_done(self, code, out, net, ask_on_fail):
        if code == 0:
            self.log(f"[OK] Wi-Fi connected to {net['ssid']}")
            self.show_list()
            self.rescan()
        elif ask_on_fail and net["secure"]:
            self.log(f"[FAIL] Wi-Fi {net['ssid']}: saved profile failed, asking for password")
            self.show_password(net)
            self.set_status("Saved password failed, enter it again", "red")
        else:
            self.log(f"[FAIL] Wi-Fi {net['ssid']}: {out}")
            self.set_status(f"Failed: {out[-60:]}", "red")

    def disconnect(self):
        self.set_status("Disconnecting...", "orange")

        def task():
            code, out = nmcli("dev", "disconnect", "wlan0")
            self.log(f"[{'OK' if code == 0 else 'FAIL'}] Wi-Fi disconnect: {out}")
            self.ui(self.rescan)

        threading.Thread(target=task, daemon=True).start()

    def close(self):
        self.win.destroy()
        if self.on_close:
            self.on_close()
