import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import os
import sys
import threading
import re
import time

from wifi_dialog import WifiDialog, wifi_status

BASE_DIR = "/home/muk0015/diploma_project"
UPS_STATUS = "/run/ups/status"
WELCOME_BG = os.path.join(BASE_DIR, "assets", "welcome_bg.png")
AUTO_LOCK_S = 600
SCREEN_OFF_S = 30
# Exit code that tells ~/.xinitrc to start the desktop instead of restarting the GUI
SERVICE_EXIT = 3
if os.path.exists(BASE_DIR):
    os.chdir(BASE_DIR)

class AnalyzerApp:
    PORTS = {
        "MONITOR": {"ns": "analyzer_monitor", "iface": "eth1", "net4": "10.0.1.0/24",
                    "v4": "10.0.1.20", "v6": "fd00:1::20"},
        "SENDER": {"ns": "analyzer_sender", "iface": "eth2", "net4": "10.0.2.0/24",
                   "v4": "10.0.2.20", "v6": "fd00:2::20"},
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Portable Network Analyzer")
        self.root.geometry("800x480")
        # Kiosk mode: no title bar to hit on a resistive touchscreen
        self.root.attributes('-fullscreen', True)
        self.root.config(cursor="none")

        self.stats = {"TCP": 0, "UDP": 0, "ICMP": 0}
        self.is_monitoring = False
        self.sniff_process = None
        self.test_running = False
        self.found = {}
        self.welcome = self.catcher = self.wifi = None
        self.welcome_gen = 0
        self.locked = self.screen_off = False
        self.last_touch = time.monotonic()

        self.setup_ui()
        self.show_welcome()
        self.root.bind_all("<ButtonPress>", self.touched, add="+")
        try:
            # DPMS on with zero timeouts: the screen goes off only when locked
            subprocess.run(["xset", "+dpms", "dpms", "0", "0", "0"], timeout=5)
        except (OSError, subprocess.SubprocessError):
            pass
        self.root.after(5000, self.idle_check)

    def setup_ui(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        btn_cfg = {'font': ('Arial', 10, 'bold'), 'height': 2, 'width': 14}

        self.btn_dhcp = tk.Button(btn_frame, fg="white", command=self.toggle_dhcp, **btn_cfg)
        self.btn_dhcp.grid(row=0, column=0, padx=5, pady=2)
        self.dhcp_on = subprocess.run(["pgrep", "-x", "dnsmasq"], capture_output=True).returncode == 0
        self.show_dhcp()
        tk.Button(btn_frame, text="2. ARP SCAN", bg="#2196F3", fg="white", command=self.run_arp_scan, **btn_cfg).grid(row=0, column=1, padx=5, pady=2)
        self.btn_monitor = tk.Button(btn_frame, text="3. LIVE STATS", bg="#607D8B", fg="white", command=self.toggle_monitoring, **btn_cfg)
        self.btn_monitor.grid(row=0, column=2, padx=5, pady=2)
        tk.Button(btn_frame, text="SYSTEM", bg="#37474F", fg="white", command=self.system_menu, **btn_cfg).grid(row=0, column=3, padx=5, pady=2)

        tk.Button(btn_frame, text="SPEED v4", bg="#9C27B0", fg="white", command=self.run_iperf_v4, **btn_cfg).grid(row=1, column=0, padx=5, pady=2)
        tk.Button(btn_frame, text="PING v4", bg="#FF5722", fg="white", command=self.run_ping_v4, **btn_cfg).grid(row=1, column=1, padx=5, pady=2)
        tk.Button(btn_frame, text="SPEED v6", bg="#6A1B9A", fg="white", command=self.run_iperf_v6, **btn_cfg).grid(row=1, column=2, padx=5, pady=2)
        tk.Button(btn_frame, text="PING v6", bg="#E64A19", fg="white", command=self.run_ping_v6, **btn_cfg).grid(row=1, column=3, padx=5, pady=2)

        # --- Security & Recon (NMAP) Section ---
        sec_frame = tk.LabelFrame(self.root, text=" Security & Recon (Nmap) ", font=('Arial', 10, 'bold'), fg="darkred")
        sec_frame.pack(fill=tk.X, padx=10, pady=2)

        tk.Label(sec_frame, text="Target IP:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.ip_entry = tk.Entry(sec_frame, font=('Arial', 11), width=15)
        self.ip_entry.insert(0, "10.0.2.20")
        self.ip_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(sec_frame, text="DET", bg="#FFC107", font=('Arial', 9, 'bold'), pady=8, command=self.detect_gateway).pack(side=tk.LEFT, padx=2)

        self.scan_mode = tk.StringVar(value="LAN")
        tk.Radiobutton(sec_frame, text="LAN", variable=self.scan_mode, value="LAN", font=('Arial', 9), pady=8).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(sec_frame, text="Wi-Fi", variable=self.scan_mode, value="WIFI", font=('Arial', 9), pady=8).pack(side=tk.LEFT, padx=2)

        tk.Button(sec_frame, text="SCAN", bg="#333333", fg="white", font=('Arial', 9, 'bold'), pady=8, command=self.run_nmap, width=8).pack(side=tk.LEFT, padx=5)
        
        # Custom Numpad trigger
        tk.Button(sec_frame, text="NUMPAD", bg="#009688", fg="white", font=('Arial', 9, 'bold'), pady=8, command=self.toggle_numpad).pack(side=tk.RIGHT, padx=5)

        # --- IPv6 Audit and Target Discovery Section ---
        ra_frame = tk.LabelFrame(self.root, text=" IPv6 Audit & Target Discovery ", font=('Arial', 10, 'bold'), fg="darkgreen")
        ra_frame.pack(fill=tk.X, padx=10, pady=2)

        tk.Label(ra_frame, text="Port:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.ra_port = tk.StringVar(value="SENDER")
        tk.Radiobutton(ra_frame, text="Monitor eth1", variable=self.ra_port, value="MONITOR", font=('Arial', 9), pady=8).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(ra_frame, text="Sender eth2", variable=self.ra_port, value="SENDER", font=('Arial', 9), pady=8).pack(side=tk.LEFT, padx=2)

        tk.Button(ra_frame, text="RA SCAN", bg="#00695C", fg="white", font=('Arial', 9, 'bold'), pady=8, command=self.run_ra_audit, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(ra_frame, text="NEIGHBORS", bg="#0277BD", fg="white", font=('Arial', 9, 'bold'), pady=8, command=self.run_neigh_scan, width=11).pack(side=tk.LEFT, padx=2)

        # --- Dashboard Section ---
        self.res_frame = tk.LabelFrame(self.root, text=" Intelligence Dashboard ", font=('Arial', 10, 'bold'), fg="darkblue")
        self.res_frame.pack(fill=tk.X, padx=10, pady=2)

        self.lbl_speed = tk.Label(self.res_frame, text="Speed: -- Mbps", font=('Arial', 12, 'bold'))
        self.lbl_speed.pack(side=tk.LEFT, padx=20)
        self.lbl_icmp = tk.Label(self.res_frame, text="Live ICMP/6: 0", font=('Arial', 12), fg="red")
        self.lbl_icmp.pack(side=tk.LEFT, padx=20)
        self.lbl_ra = tk.Label(self.res_frame, text="RA routers: --", font=('Arial', 12))
        self.lbl_ra.pack(side=tk.LEFT, padx=20)
        self.lbl_bat = tk.Label(self.res_frame, text="Battery: --", font=('Arial', 12, 'bold'), fg="gray")
        self.lbl_bat.pack(side=tk.RIGHT, padx=10)
        self.update_battery()

        self.log_area = scrolledtext.ScrolledText(self.root, width=90, height=8, font=('Consolas', 9))
        self.log_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    # Tk widgets must only be touched from the main thread
    def ui(self, fn, *args, **kwargs):
        self.root.after(0, lambda: fn(*args, **kwargs))

    def log(self, text):
        self.ui(self._append_log, text)

    def _append_log(self, text):
        self.log_area.insert(tk.END, f"{text}\n")
        self.log_area.see(tk.END)

    def detect_gateway(self):
        try:
            res = subprocess.run("ip route | grep default", shell=True, capture_output=True, text=True)
            match = re.search(r"via ([\d\.]+)", res.stdout)
            if match:
                gw = match.group(1)
                self.ip_entry.delete(0, tk.END)
                self.ip_entry.insert(0, gw)
                self.log(f"System: Detected Gateway {gw}")
            else:
                self.log("System: Gateway not found.")
        except: pass

    # --- Custom Numpad Implementation ---
    def toggle_numpad(self):
        if hasattr(self, 'numpad') and self.numpad.winfo_exists():
            self.numpad.destroy()
            return

        self.numpad = tk.Toplevel(self.root)
        self.numpad.title("IP Numpad")
        self.numpad.geometry("240x300+540+150")
        self.numpad.attributes('-topmost', True)
        self.numpad.configure(bg="#ECEFF1")

        keys = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '0', '.', 'DEL']

        row_idx, col_idx = 0, 0
        for key in keys:
            action = lambda x=key: self.numpad_press(x)
            btn = tk.Button(self.numpad, text=key, font=('Arial', 16, 'bold'), command=action, height=2, width=4)
            btn.grid(row=row_idx, column=col_idx, padx=5, pady=5)
            col_idx += 1
            if col_idx > 2:
                col_idx = 0
                row_idx += 1

        tk.Button(self.numpad, text="CLEAR", font=('Arial', 12, 'bold'), bg="#f44336", fg="white", command=lambda: self.ip_entry.delete(0, tk.END), height=2).grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="we")
        tk.Button(self.numpad, text="OK", font=('Arial', 12, 'bold'), bg="#4CAF50", fg="white", command=self.numpad.destroy, height=2).grid(row=row_idx, column=2, padx=5, pady=5, sticky="we")

    def numpad_press(self, key):
        if key == 'DEL':
            current = self.ip_entry.get()
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, current[:-1])
        else:
            self.ip_entry.insert(tk.END, key)

    def netns_for(self, target):
        t = target.strip().lower()
        if t.startswith("10.0.1.") or t.startswith("fd00:1:"):
            return "analyzer_monitor"
        return "analyzer_sender"

    def device_macs(self):
        macs = []
        for cfg in self.PORTS.values():
            cmd = ["sudo", "ip", "netns", "exec", cfg["ns"], "cat", "/sys/class/net/%s/address" % cfg["iface"]]
            res = subprocess.run(cmd, capture_output=True, text=True)
            mac = res.stdout.strip()
            if mac:
                macs.append(mac)
        return ",".join(macs)

    def port_cfg(self):
        return self.PORTS[self.ra_port.get()]

    def target_for(self, cfg, family):
        found = self.found.get(cfg["ns"], {}).get(family)
        if found:
            return found, "discovered"
        return cfg[family], "hardcoded fallback"

    def run_neigh_scan(self):
        if self.test_running: return
        cfg = self.port_cfg()
        self.test_running = True
        self.log(f"Discovery: enumerating IPv6 neighbours on {cfg['iface']} ({cfg['ns']})...")

        def task():
            base = ["sudo", "ip", "netns", "exec", cfg["ns"]]
            cmd = base + ["python3", "neigh_scan.py", cfg["iface"]]
            own = self.device_macs()
            if own:
                cmd += ["--own", own]

            res = subprocess.run(cmd, capture_output=True, text=True)
            self.log("-" * 30)
            self.log(res.stdout.strip() if res.stdout.strip() else "No output.")
            if res.stderr.strip():
                self.log(res.stderr.strip())

            arp = subprocess.run(base + ["python3", "arp_scan.py", cfg["iface"], cfg["net4"]],
                                 capture_output=True, text=True)
            self.log(arp.stdout.strip() if arp.stdout.strip() else "No ARP output.")
            self.log("-" * 30)

            store = self.found.setdefault(cfg["ns"], {})
            m6 = re.search(r"^TARGET6\s+:\s+(\S+)", res.stdout, re.M)
            if m6 and m6.group(1) != "none":
                store["v6"] = m6.group(1)
            m4 = re.search(r"^TARGET4:\s+(\S+)", arp.stdout, re.M)
            if m4 and m4.group(1) != "none":
                store["v4"] = m4.group(1)
                self.ui(self.ip_entry.delete, 0, tk.END)
                self.ui(self.ip_entry.insert, 0, store["v4"])

            self.log(f"Discovery: targets for {cfg['ns']} -> "
                     f"v4 {store.get('v4', 'none')}, v6 {store.get('v6', 'none')}")
            self.test_running = False

        threading.Thread(target=task, daemon=True).start()

    def run_ra_audit(self):
        if self.test_running: return
        cfg = self.port_cfg()
        ns, iface = cfg["ns"], cfg["iface"]
        self.test_running = True
        self.lbl_ra.config(text="RA routers: ...", fg="orange")
        self.log(f"Audit: soliciting Router Advertisement on {iface} ({ns})...")

        def task():
            cmd = ["sudo", "ip", "netns", "exec", ns, "python3", "ra_audit.py", iface, "-t", "5"]
            own = self.device_macs()
            if own:
                cmd += ["--own", own]

            res = subprocess.run(cmd, capture_output=True, text=True)
            self.log("-" * 30)
            self.log(res.stdout.strip() if res.stdout.strip() else "No output.")
            if res.stderr.strip():
                self.log(res.stderr.strip())
            self.log("-" * 30)

            match = re.search(r"^Routers\s+:\s+(\d+)", res.stdout, re.M)
            total = int(match.group(1)) if match else 0
            foreign = res.stdout.count("[FOREIGN]")
            if foreign:
                self.ui(self.lbl_ra.config, text=f"RA routers: {total} (foreign {foreign})", fg="red")
            elif total:
                self.ui(self.lbl_ra.config, text=f"RA routers: {total}", fg="green")
            else:
                self.ui(self.lbl_ra.config, text="RA routers: none", fg="black")
            self.test_running = False

        threading.Thread(target=task, daemon=True).start()

    def run_nmap(self):
        if self.test_running: return
        target = self.ip_entry.get().strip()
        if not target:
            self.log("Error: Please enter a target IP.")
            return

        mode = self.scan_mode.get()
        self.test_running = True
        self.log(f"Recon: Starting FAST Nmap scan against {target} ({mode})...")

        def task():
            base_nmap = ["nmap", "-F", "-sV", "-T4", "--max-retries", "1", "--host-timeout", "30s", target]
            
            if mode == "LAN":
                ns = self.netns_for(target)
                self.log(f"Recon: using namespace {ns}")
                cmd = ["sudo", "ip", "netns", "exec", ns] + base_nmap
            else:
                cmd = ["sudo"] + base_nmap

            res = subprocess.run(cmd, capture_output=True, text=True)
            self.log("-" * 30)
            self.log(f"NMAP RESULTS ({mode}):")
            if res.stdout:
                self.log(res.stdout)
            else:
                self.log("No response or scan timed out.")
            self.log("-" * 30)
            self.test_running = False

        threading.Thread(target=task, daemon=True).start()

    # Ports are set up at boot by analyzer-ports.service; serving DHCP and RA
    # is opt-in, so the device is safe to plug into a foreign network
    def show_dhcp(self):
        if self.dhcp_on:
            self.btn_dhcp.config(text="1. DHCP: ON", bg="#4CAF50")
        else:
            self.btn_dhcp.config(text="1. DHCP: OFF", bg="#9E9E9E")

    def toggle_dhcp(self):
        mode = "nodhcp" if self.dhcp_on else "dhcp"
        self.log(f"System: {'stopping' if self.dhcp_on else 'starting'} DHCP and RA on both ports...")

        def task():
            r = subprocess.run(["sudo", "./setup_network.sh", mode], capture_output=True, text=True)
            out = (r.stdout + r.stderr).strip()
            if r.returncode == 0:
                self.dhcp_on = mode == "dhcp"
                self.log(f"[OK] {out}")
            else:
                self.log(f"[FAIL] setup_network.sh {mode}: {out}")
            self.ui(self.show_dhcp)

        threading.Thread(target=task, daemon=True).start()

    def execute_iperf(self, target, proto_name, ns=None):
        if self.test_running: return
        self.log(f"Test: Running throughput test to {target} ({proto_name})...")
        self.lbl_speed.config(text="Testing...", fg="orange")
        self.test_running = True

        def task():
            cmd = ["sudo", "ip", "netns", "exec", ns or self.netns_for(target), "iperf3", "-c", target, "-t", "5"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if "error" in res.stderr or "error" in res.stdout:
                self.log(res.stderr if res.stderr else res.stdout)

            match = re.findall(r"([\d\.]+)\s+Mbits/sec\s+receiver", res.stdout)
            if not match: match = re.findall(r"([\d\.]+)\s+Mbits/sec", res.stdout)

            if match:
                mbps = match[-1]
                self.ui(self.lbl_speed.config, text=f"Speed: {mbps} Mbps", fg="green")
                self.log(f"[SUCCESS] {proto_name} Bandwidth: {mbps} Mbps")
            else:
                self.ui(self.lbl_speed.config, text="Fail", fg="red")
            self.test_running = False

        threading.Thread(target=task, daemon=True).start()

    def run_iperf_v4(self):
        cfg = self.port_cfg()
        target, source = self.target_for(cfg, "v4")
        self.log(f"Target: {target} ({source})")
        self.execute_iperf(target, "IPv4", ns=cfg["ns"])

    def run_iperf_v6(self):
        cfg = self.port_cfg()
        target, source = self.target_for(cfg, "v6")
        self.log(f"Target: {target} ({source})")
        self.execute_iperf(target, "IPv6", ns=cfg["ns"])

    def execute_ping(self, target, is_ipv6=False, ns=None):
        if self.test_running: return
        proto = "IPv6" if is_ipv6 else "IPv4"
        self.log(f"Test: Measuring {proto} latency to {target}...")
        self.test_running = True

        def task():
            ping_cmd = "ping" if not is_ipv6 else "ping6"
            cmd = ["sudo", "ip", "netns", "exec", ns or self.netns_for(target), ping_cmd, target, "-c", "4"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.log("-" * 20)
            self.log(res.stdout)

            if res.returncode == 0:
                self.log(f"[SUCCESS] {proto} Target is reachable.")
            else:
                self.log(f"[FAILED] No response from {proto} target.")
            self.test_running = False

        threading.Thread(target=task, daemon=True).start()

    def run_ping_v4(self):
        cfg = self.port_cfg()
        target, source = self.target_for(cfg, "v4")
        self.log(f"Target: {target} ({source})")
        self.execute_ping(target, is_ipv6=False, ns=cfg["ns"])

    def run_ping_v6(self):
        cfg = self.port_cfg()
        target, source = self.target_for(cfg, "v6")
        self.log(f"Target: {target} ({source})")
        self.execute_ping(target, is_ipv6=True, ns=cfg["ns"])

    def run_arp_scan(self):
        cfg = self.port_cfg()
        self.log(f"Scan: ARP sweep of {cfg['net4']} on {cfg['iface']} ({cfg['ns']})...")
        cmd = ["sudo", "ip", "netns", "exec", cfg["ns"], "python3", "arp_scan.py", cfg["iface"], cfg["net4"]]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.log(res.stdout)

    def toggle_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.btn_monitor.config(text="STOP STATS", bg="#FF9800")
            self.log("Monitor: Passive capture on eth1 (IPv4/v6)...")
            self.stats = {"TCP": 0, "UDP": 0, "ICMP": 0}
            threading.Thread(target=self.packet_sniff_thread, daemon=True).start()
            self.update_labels()
        else:
            self.is_monitoring = False
            self.btn_monitor.config(text="3. LIVE STATS", bg="#607D8B")
            if self.sniff_process: self.sniff_process.terminate()

    def packet_sniff_thread(self):
        cmd = ["sudo", "ip", "netns", "exec", "analyzer_monitor", "tcpdump", "-i", "eth1", "-n", "-l"]
        try:
            self.sniff_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            for line in self.sniff_process.stdout:
                if not self.is_monitoring: break
                l = line.upper()
                if "ICMP" in l or "ICMP6" in l: self.stats["ICMP"] += 1
                elif "TCP" in l: self.stats["TCP"] += 1
                elif "UDP" in l: self.stats["UDP"] += 1
        except: pass

    def update_labels(self):
        if self.is_monitoring:
            self.lbl_icmp.config(text=f"Live ICMP/6: {self.stats['ICMP']}")
            self.root.after(500, self.update_labels)

    # Written every 10 s by the ups-monitor service; stale means the service is down
    def battery_text(self):
        try:
            if time.time() - os.path.getmtime(UPS_STATUS) < 30:
                with open(UPS_STATUS) as f:
                    fields = dict(re.findall(r"(\w+)=(\S+)", f.read()))
                pct = int(fields["PCT"])
                src = fields.get("SRC", "BAT")
                if src != "BAT":
                    return f"{pct}% {'charging' if src == 'CHG' else 'AC'}", "darkgreen"
                mins = fields.get("MIN", "-")
                left = f" ~{int(mins) // 60}h{int(mins) % 60:02d}" if mins.isdigit() else ""
                low = pct < 10 or fields.get("LOW", "0") != "0"
                return f"{pct}%{left}", "red" if low else "orange" if pct < 25 else "green"
        except (OSError, KeyError, ValueError):
            pass
        return "--", "gray"

    def update_battery(self):
        text, color = self.battery_text()
        self.lbl_bat.config(text=f"Battery: {text}", fg=color)
        self.root.after(5000, self.update_battery)

    # Welcome screen doubles as the lock screen; drawn on a canvas so text sits on the wallpaper
    def show_welcome(self, locked=False):
        if self.welcome is not None and self.welcome.winfo_exists():
            self.btn_start.config(text="UNLOCK" if locked else "START")
            return
        self.welcome_gen += 1
        c = tk.Canvas(self.root, width=800, height=480, bg="#0B2A30", highlightthickness=0, cursor="none")
        c.place(x=0, y=0, relwidth=1, relheight=1)
        self.welcome = c
        try:
            self.bg_image = tk.PhotoImage(file=WELCOME_BG)
            c.create_image(0, 0, image=self.bg_image, anchor="nw")
        except tk.TclError:
            pass

        x = 480
        c.create_text(x, 40, text="Portable Network", font=('Arial', 24, 'bold'), fill="white", anchor="nw")
        c.create_text(x, 72, text="Analyzer", font=('Arial', 24, 'bold'), fill="white", anchor="nw")
        c.create_text(x, 114, text="Testing and monitoring networks", font=('Arial', 11), fill="#9FC5C9", anchor="nw")
        self.welcome_info = {}
        for i, key in enumerate(("Battery", "Ports", "Wi-Fi")):
            y = 156 + i * 24
            c.create_text(x, y, text=key, font=('Arial', 11), fill="#7FA7AD", anchor="nw")
            self.welcome_info[key] = c.create_text(x + 68, y, text="...", font=('Arial', 11), fill="white", anchor="nw")

        self.btn_start = tk.Button(c, text="UNLOCK" if locked else "START", bg="#43A047", fg="white", bd=0,
                                   activebackground="#2E7D32", font=('Arial', 18, 'bold'), command=self.unlock)
        c.create_window(x, 240, window=self.btn_start, anchor="nw", width=300, height=60)
        wifi = tk.Button(c, text="WI-FI", bg="#0277BD", fg="white", bd=0, font=('Arial', 12, 'bold'), command=self.open_wifi)
        c.create_window(x, 312, window=wifi, anchor="nw", width=145, height=46)
        off = tk.Button(c, text="POWER OFF", bg="#E53935", fg="white", bd=0, font=('Arial', 12, 'bold'), command=self.power_off)
        c.create_window(x + 155, 312, window=off, anchor="nw", width=145, height=46)
        c.create_text(12, 468, text="Mikhail Mukanov  |  2027", font=('Arial', 9), fill="#5E8A90", anchor="w")
        self.update_welcome(self.welcome_gen)

    def update_welcome(self, gen):
        if gen != self.welcome_gen or self.welcome is None:
            return

        def task():
            ports = []
            for cfg in self.PORTS.values():
                r = subprocess.run(["sudo", "ip", "-n", cfg["ns"], "-br", "link", "show", cfg["iface"]], capture_output=True, text=True)
                fields = r.stdout.split()
                state = "not set up" if r.returncode != 0 or len(fields) < 2 else "up" if fields[1] == "UP" else "no link"
                ports.append(f"{cfg['iface']} {state}")
            ssid, ip = wifi_status()
            values = {"Battery": self.battery_text()[0],
                      "Ports": f"{', '.join(ports)}, DHCP {'on' if self.dhcp_on else 'off'}",
                      "Wi-Fi": f"{ssid} ({ip or 'no IP'})" if ssid else "not connected"}
            self.ui(self.show_welcome_info, gen, values)

        threading.Thread(target=task, daemon=True).start()
        self.root.after(3000, self.update_welcome, gen)

    def show_welcome_info(self, gen, values):
        if gen == self.welcome_gen and self.welcome is not None:
            for key, text in values.items():
                self.welcome.itemconfig(self.welcome_info[key], text=text)

    def unlock(self):
        self.locked = False
        if self.welcome is not None:
            self.welcome.destroy()
            self.welcome = None

    # Screen off is DPMS through X: saves 0.35 W of 4.5 W (measured 26.09.2026);
    # the backlight has only a mechanical switch and stays lit
    def touched(self, event=None):
        self.last_touch = time.monotonic()

    def idle_check(self):
        idle = time.monotonic() - self.last_touch
        if not self.locked and idle > AUTO_LOCK_S:
            self.lock()
        elif self.locked and not self.screen_off and idle > SCREEN_OFF_S:
            self.display(False)
        self.root.after(5000, self.idle_check)

    def lock(self):
        self.close_menu()
        for win in (getattr(self, 'numpad', None), self.wifi.win if self.wifi else None):
            if win is not None and win.winfo_exists():
                win.destroy()
        self.locked = True
        self.show_welcome(locked=True)
        self.display(False)

    def display(self, on):
        self.screen_off = not on
        if on:
            if self.catcher is not None:
                self.catcher.destroy()
                self.catcher = None
        elif self.catcher is None:
            # Swallows the waking tap so it cannot press a button on the lock screen
            self.catcher = tk.Frame(self.root, bg="black", cursor="none")
            self.catcher.place(x=0, y=0, relwidth=1, relheight=1)
            self.catcher.bind("<ButtonPress>", lambda e: self.display(True))
        try:
            subprocess.run(["xset", "dpms", "force", "on" if on else "off"], timeout=5)
        except (OSError, subprocess.SubprocessError):
            pass

    def system_menu(self):
        if hasattr(self, 'menu') and self.menu.winfo_exists():
            self.menu.destroy()
            return

        self.menu = tk.Toplevel(self.root)
        self.menu.title("System")
        self.menu.geometry("360x325+220+75")
        self.menu.attributes('-topmost', True)
        self.menu.configure(bg="#ECEFF1", cursor="none")

        cfg = {'font': ('Arial', 12, 'bold'), 'height': 2, 'width': 26}
        tk.Button(self.menu, text="LOCK SCREEN", bg="#37474F", fg="white", command=self.lock, **cfg).pack(padx=10, pady=(12, 5))
        tk.Button(self.menu, text="WI-FI", bg="#0277BD", fg="white", command=self.open_wifi, **cfg).pack(padx=10, pady=5)
        tk.Button(self.menu, text="POWER OFF", bg="#f44336", fg="white", command=self.power_off, **cfg).pack(padx=10, pady=5)
        tk.Button(self.menu, text="SERVICE MODE (DESKTOP)", bg="#607D8B", fg="white", command=lambda: self.close_app(SERVICE_EXIT), **cfg).pack(padx=10, pady=5)
        tk.Button(self.menu, text="CANCEL", command=self.menu.destroy, **cfg).pack(padx=10, pady=5)

    def close_menu(self):
        if hasattr(self, 'menu') and self.menu.winfo_exists():
            self.menu.destroy()

    def open_wifi(self):
        self.close_menu()
        self.wifi = WifiDialog(self.root, self.log)

    def stop_sniffer(self):
        self.is_monitoring = False
        if self.sniff_process: self.sniff_process.terminate()

    def power_off(self):
        self.close_menu()
        self.stop_sniffer()
        self.log("Shutting down...")
        subprocess.Popen(["sudo", "shutdown", "-h", "now"])

    def close_app(self, code=0):
        self.stop_sniffer()
        self.root.destroy()
        sys.exit(code)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnalyzerApp(root)
    root.mainloop()