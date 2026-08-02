import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import os
import sys
import threading
import re

BASE_DIR = "/home/muk0015/diploma_project"
if os.path.exists(BASE_DIR):
    os.chdir(BASE_DIR)

class AnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Portable Network Analyzer")
        self.root.geometry("800x480")

        self.stats = {"TCP": 0, "UDP": 0, "ICMP": 0}
        self.is_monitoring = False
        self.sniff_process = None
        self.test_running = False

        self.setup_ui()

    def setup_ui(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        btn_cfg = {'font': ('Arial', 10, 'bold'), 'height': 2, 'width': 14}

        tk.Button(btn_frame, text="1. SETUP NET", bg="#4CAF50", fg="white", command=self.run_setup, **btn_cfg).grid(row=0, column=0, padx=5, pady=2)
        tk.Button(btn_frame, text="2. ARP SCAN", bg="#2196F3", fg="white", command=self.run_arp_scan, **btn_cfg).grid(row=0, column=1, padx=5, pady=2)
        self.btn_monitor = tk.Button(btn_frame, text="3. LIVE STATS", bg="#607D8B", fg="white", command=self.toggle_monitoring, **btn_cfg)
        self.btn_monitor.grid(row=0, column=2, padx=5, pady=2)
        tk.Button(btn_frame, text="EXIT", bg="#f44336", fg="white", command=self.close_app, **btn_cfg).grid(row=0, column=3, padx=5, pady=2)

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
        
        tk.Button(sec_frame, text="DET", bg="#FFC107", font=('Arial', 8, 'bold'), command=self.detect_gateway).pack(side=tk.LEFT, padx=2)

        self.scan_mode = tk.StringVar(value="LAN")
        tk.Radiobutton(sec_frame, text="LAN", variable=self.scan_mode, value="LAN", font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(sec_frame, text="Wi-Fi", variable=self.scan_mode, value="WIFI", font=('Arial', 9)).pack(side=tk.LEFT, padx=2)

        tk.Button(sec_frame, text="SCAN", bg="#333333", fg="white", font=('Arial', 9, 'bold'), command=self.run_nmap, width=8).pack(side=tk.LEFT, padx=5)
        
        # Custom Numpad trigger
        tk.Button(sec_frame, text="NUMPAD", bg="#009688", fg="white", font=('Arial', 9, 'bold'), command=self.toggle_numpad).pack(side=tk.RIGHT, padx=5)

        # --- Dashboard Section ---
        self.res_frame = tk.LabelFrame(self.root, text=" Intelligence Dashboard ", font=('Arial', 10, 'bold'), fg="darkblue")
        self.res_frame.pack(fill=tk.X, padx=10, pady=2)

        self.lbl_speed = tk.Label(self.res_frame, text="Speed: -- Mbps", font=('Arial', 12, 'bold'))
        self.lbl_speed.pack(side=tk.LEFT, padx=20)
        self.lbl_icmp = tk.Label(self.res_frame, text="Live ICMP/6: 0", font=('Arial', 12), fg="red")
        self.lbl_icmp.pack(side=tk.LEFT, padx=20)

        self.log_area = scrolledtext.ScrolledText(self.root, width=90, height=8, font=('Consolas', 9))
        self.log_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def log(self, text):
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

    def run_setup(self):
        self.log("System: Refreshing network namespaces (IPv4 & IPv6)...")
        subprocess.run(["sudo", "./setup_network.sh"])
        self.log("[OK] Netns and DHCP servers are ready.")

    def execute_iperf(self, target, proto_name):
        if self.test_running: return
        self.log(f"Test: Running throughput test to {target} ({proto_name})...")
        self.lbl_speed.config(text="Testing...", fg="orange")
        self.test_running = True

        def task():
            cmd = ["sudo", "ip", "netns", "exec", self.netns_for(target), "iperf3", "-c", target, "-t", "5"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if "error" in res.stderr or "error" in res.stdout:
                self.log(res.stderr if res.stderr else res.stdout)

            match = re.findall(r"([\d\.]+)\s+Mbits/sec\s+receiver", res.stdout)
            if not match: match = re.findall(r"([\d\.]+)\s+Mbits/sec", res.stdout)

            if match:
                mbps = match[-1]
                self.lbl_speed.config(text=f"Speed: {mbps} Mbps", fg="green")
                self.log(f"[SUCCESS] {proto_name} Bandwidth: {mbps} Mbps")
            else:
                self.lbl_speed.config(text="Fail", fg="red")
            self.test_running = False

        threading.Thread(target=task, daemon=True).start()

    def run_iperf_v4(self):
        self.execute_iperf("10.0.2.20", "IPv4")

    def run_iperf_v6(self):
        self.execute_iperf("fd00:2::20", "IPv6")

    def execute_ping(self, target, is_ipv6=False):
        if self.test_running: return
        proto = "IPv6" if is_ipv6 else "IPv4"
        self.log(f"Test: Measuring {proto} latency to {target}...")
        self.test_running = True

        def task():
            ping_cmd = "ping" if not is_ipv6 else "ping6"
            cmd = ["sudo", "ip", "netns", "exec", self.netns_for(target), ping_cmd, target, "-c", "4"]
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
        self.execute_ping("10.0.2.20", is_ipv6=False)

    def run_ping_v6(self):
        self.execute_ping("fd00:2::20", is_ipv6=True)

    def run_arp_scan(self):
        self.log("Scan: Scanning 10.0.2.x subnet...")
        cmd = ["sudo", "ip", "netns", "exec", "analyzer_sender", "python3", "arp_scan.py"]
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

    def close_app(self):
        self.is_monitoring = False
        if self.sniff_process: self.sniff_process.terminate()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = AnalyzerApp(root)
    root.mainloop()