# Состояние устройства: код, конфиги, логи

Сырые выгрузки с Raspberry Pi из чата Gemini (в хронологическом порядке).

Актуальный код — в GitHub-репозитории, здесь только история и контекст.


## Ход [8]

```
muk0015@raspberrypi:~/diploma_project$ ls

arp_scan.py  capture.pcap  gui_app.py  setup_network.sh

muk0015@raspberrypi:~/diploma_project$ cat setup_network.sh

#!/bin/bash




# Очистка

ip netns delete analyzer_monitor 2>/dev/null

ip netns delete analyzer_sender 2>/dev/null




# Создание пространств

ip netns add analyzer_monitor

ip netns add analyzer_sender




# Перемещение интерфейсов

ip link set dev eth1 netns analyzer_monitor

ip link set dev eth2 netns analyzer_sender




# Настройка Monitor (eth1)

ip netns exec analyzer_monitor ip addr add 10.0.1.10/24 dev eth1

ip netns exec analyzer_monitor ip link set eth1 up

ip netns exec analyzer_monitor ip link set lo up




# Настройка Sender (eth2)

ip netns exec analyzer_sender ip addr add 10.0.2.10/24 dev eth2

ip netns exec analyzer_sender ip link set eth2 up

ip netns exec analyzer_sender ip link set lo up




echo "Network setup complete. Isolated modes active."

muk0015@raspberrypi:~/diploma_project$

сорян забыл, короче щас я беру все это и иду в университет к преподу там подключу к пк в лабе и надо будет рассказать и продемонстрировать че и как у меня работает, думаю твоя помощь и советы мне понадобятся. если что-то не будет получаться то я буду обращаться за помощью к тебе
```


## Ход [34]

```
я изменил скрипт так как ты сказал и сделал все то что ты описывал:

muk0015@raspberrypi:~$ nano setup_network.sh

muk0015@raspberrypi:~$ ды

-bash: ды: command not found

muk0015@raspberrypi:~$ ls

captures         Documents     LCD-show      Pictures       Templates

Desktop          Downloads     Music         Public         Videos

diploma_project  generator.py  network_logs  scapy_project

muk0015@raspberrypi:~$ cd diploma_project/

muk0015@raspberrypi:~/diploma_project$ ls

arp_scan.py  capture.pcap  gui_app.py  setup_network.sh

muk0015@raspberrypi:~/diploma_project$ nano setup_network.sh

muk0015@raspberrypi:~/diploma_project$ sudo ./setup_network.sh

Network setup complete. IPv4 and IPv6 isolated modes active.

muk0015@raspberrypi:~/diploma_project$

и вот такой вот вывод получился на пк в лабе, то есть ниче несработало student@pc15:~$ ip a

1: lo: mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000

link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00

inet 127.0.0.1/8 scope host lo

valid_lft forever preferred_lft forever

inet6 ::1/128 scope host noprefixroute

valid_lft forever preferred_lft forever

2: enp3s0: mtu 1500 qdisc fq_codel state UP group default qlen 1000

link/ether d0:f4:05:3a:ce:35 brd ff:ff:ff:ff:ff:ff

inet6 2001:718:1001:2c8:b01d:6c30:11ca:5bcc/64 scope global temporary dynamic

valid_lft 89385sec preferred_lft 85406sec

inet6 2001:718:1001:2c8:d2f4:5ff:fe3a:ce35/64 scope global dynamic mngtmpaddr noprefixroute

valid_lft 2592000sec preferred_lft 604800sec

inet6 fe80::d2f4:5ff:fe3a:ce35/64 scope link

valid_lft forever preferred_lft forever

3: enp1s0: mtu 1500 qdisc noop state DOWN group default qlen 1000

link/ether 3c:8c:f8:60:fb:cd brd ff:ff:ff:ff:ff:ff

4: virbr0: mtu 1500 qdisc noqueue state DOWN group default qlen 1000

link/ether 52:54:00:27:72:17 brd ff:ff:ff:ff:ff:ff

inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0

valid_lft forever preferred_lft forever

6: enx00e04c382845: mtu 1500 qdisc noop state DOWN group default qlen 1000

link/ether 00:e0:4c:38:28:45 brd ff:ff:ff:ff:ff:ff

7: enx00e04c680216: mtu 1500 qdisc noop state DOWN group default qlen 1000

link/ether 00:e0:4c:68:02:16 brd ff:ff:ff:ff:ff:ff

student@pc15:~$
```


## Ход [36]

```
чтож, ладно, я поднял порты: student@pc15:~$ sudo ip link set enx00e04c382845 up

[sudo] password for student:

student@pc15:~$ sudo ip link set enx00e04c680216 up

student@pc15:~$ ip a

1: lo: mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000

link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00

inet 127.0.0.1/8 scope host lo

valid_lft forever preferred_lft forever

inet6 ::1/128 scope host noprefixroute

valid_lft forever preferred_lft forever

2: enp3s0: mtu 1500 qdisc fq_codel state UP group default qlen 1000

link/ether d0:f4:05:3a:ce:35 brd ff:ff:ff:ff:ff:ff

inet6 2001:718:1001:2c8:b01d:6c30:11ca:5bcc/64 scope global temporary dynamic

valid_lft 88854sec preferred_lft 84875sec

inet6 2001:718:1001:2c8:d2f4:5ff:fe3a:ce35/64 scope global dynamic mngtmpaddr noprefixroute

valid_lft 2592000sec preferred_lft 604800sec

inet6 fe80::d2f4:5ff:fe3a:ce35/64 scope link

valid_lft forever preferred_lft forever

3: enp1s0: mtu 1500 qdisc noop state DOWN group default qlen 1000

link/ether 3c:8c:f8:60:fb:cd brd ff:ff:ff:ff:ff:ff

4: virbr0: mtu 1500 qdisc noqueue state DOWN group default qlen 1000

link/ether 52:54:00:27:72:17 brd ff:ff:ff:ff:ff:ff

inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0

valid_lft forever preferred_lft forever

6: enx00e04c382845: mtu 1500 qdisc fq_codel state UP group default qlen 1000

link/ether 00:e0:4c:38:28:45 brd ff:ff:ff:ff:ff:ff

inet6 fe80::2e0:4cff:fe38:2845/64 scope link

valid_lft forever preferred_lft forever

7: enx00e04c680216: mtu 1500 qdisc fq_codel state UP group default qlen 1000

link/ether 00:e0:4c:68:02:16 brd ff:ff:ff:ff:ff:ff

inet6 fe80::2e0:4cff:fe68:216/64 scope link

valid_lft forever preferred_lft forever и даже заново запустил скрипт:

muk0015@raspberrypi:~/diploma_project$ sudo ./setup_network.sh

Network setup complete. IPv4 and IPv6 isolated modes active.

muk0015@raspberrypi:~/diploma_project$

но нихуя не изменилось, вот вывод после всего сделанного: student@pc15:~$ ip a

1: lo: mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000

link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00

inet 127.0.0.1/8 scope host lo

valid_lft forever preferred_lft forever

inet6 ::1/128 scope host noprefixroute

valid_lft forever preferred_lft forever

2: enp3s0: mtu 1500 qdisc fq_codel state UP group default qlen 1000

link/ether d0:f4:05:3a:ce:35 brd ff:ff:ff:ff:ff:ff

inet6 2001:718:1001:2c8:b01d:6c30:11ca:5bcc/64 scope global temporary dynamic

valid_lft 88727sec preferred_lft 84748sec

inet6 2001:718:1001:2c8:d2f4:5ff:fe3a:ce35/64 scope global dynamic mngtmpaddr noprefixroute

valid_lft 2591995sec preferred_lft 604795sec

inet6 fe80::d2f4:5ff:fe3a:ce35/64 scope link

valid_lft forever preferred_lft forever

3: enp1s0: mtu 1500 qdisc noop state DOWN group default qlen 1000

link/ether 3c:8c:f8:60:fb:cd brd ff:ff:ff:ff:ff:ff

4: virbr0: mtu 1500 qdisc noqueue state DOWN group default qlen 1000

link/ether 52:54:00:27:72:17 brd ff:ff:ff:ff:ff:ff

inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0

valid_lft forever preferred_lft forever

6: enx00e04c382845: mtu 1500 qdisc fq_codel state UP group default qlen 1000

link/ether 00:e0:4c:38:28:45 brd ff:ff:ff:ff:ff:ff

inet6 fe80::2e0:4cff:fe38:2845/64 scope link

valid_lft forever preferred_lft forever

7: enx00e04c680216: mtu 1500 qdisc fq_codel state UP group default qlen 1000

link/ether 00:e0:4c:68:02:16 brd ff:ff:ff:ff:ff:ff

inet6 fe80::2e0:4cff:fe68:216/64 scope link

valid_lft forever preferred_lft forever

student@pc15:~$
```


## Ход [38]

```
muk0015@raspberrypi:~/diploma_project$ cat gui_app.py

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

        self.test_running = False # Флаг для блокировки одновременных тестов




        self.setup_ui()




    def setup_ui(self):

        btn_frame = tk.Frame(self.root)

        btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        btn_cfg = {'font': ('Arial', 11, 'bold'), 'height': 2, 'width': 16}




        tk.Button(btn_frame, text="1. SETUP NET", bg="#4CAF50", fg="white", command=self.run_setup, **btn_cfg).grid(row=0, column=0, padx=5, pady=2)

        tk.Button(btn_frame, text="2. ARP SCAN", bg="#2196F3", fg="white", command=self.run_arp_scan, **btn_cfg).grid(row=0, column=1, padx=5, pady=2)

        self.btn_monitor = tk.Button(btn_frame, text="3. LIVE STATS", bg="#607D8B", fg="white", command=self.toggle_monitoring, **btn_cfg)

        self.btn_monitor.grid(row=0, column=2, padx=5, pady=2)

        tk.Button(btn_frame, text="EXIT", bg="#f44336", fg="white", command=self.close_app, **btn_cfg).grid(row=0, column=3, padx=5, pady=2)




        # Ряд 2

        tk.Button(btn_frame, text="4. SPEED TEST", bg="#9C27B0", fg="white", command=self.run_active_iperf, **btn_cfg).grid(row=1, column=0, padx=5, pady=2)

        tk.Button(btn_frame, text="5. PING TEST", bg="#FF5722", fg="white", command=self.run_ping_test, **btn_cfg).grid(row=1, column=1, padx=5, pady=2)




        self.res_frame = tk.LabelFrame(self.root, text=" Intelligence Dashboard ", font=('Arial', 12, 'bold'), fg="darkblue")

        self.res_frame.pack(fill=tk.X, padx=10, pady=5)




        self.lbl_speed = tk.Label(self.res_frame, text="Speed: -- Mbps", font=('Arial', 14, 'bold'))

        self.lbl_speed.pack(side=tk.LEFT, padx=20)

        self.lbl_icmp = tk.Label(self.res_frame, text="Live ICMP/6: 0", font=('Arial', 14), fg="red")

        self.lbl_icmp.pack(side=tk.LEFT, padx=20)




        self.log_area = scrolledtext.ScrolledText(self.root, width=90, height=12, font=('Consolas', 10))

        self.log_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)




    def log(self, text):

        self.log_area.insert(tk.END, f"{text}\n")

        self.log_area.see(tk.END)




    def run_setup(self):

        self.log("System: Refreshing network namespaces...")

        subprocess.run(["sudo", "./setup_network.sh"])

        self.log("[OK] Netns ready.")




    def run_active_iperf(self):

        if self.test_running: return

        target = "10.0.2.20"

        self.log(f"Test: Running throughput test to {target}...")

        self.lbl_speed.config(text="Testing...", fg="orange")

        self.test_running = True




        def task():

            cmd = ["sudo", "ip", "netns", "exec", "analyzer_sender", "iperf3", "-c", target, "-t", "5"]

            res = subprocess.run(cmd, capture_output=True, text=True)

            self.log(res.stdout)




            # Парсинг скорости

            match = re.findall(r"([\d\.]+)\s+Mbits/sec\s+receiver", res.stdout)

            if not match: match = re.findall(r"([\d\.]+)\s+Mbits/sec", res.stdout)




            if match:

                mbps = match[-1]

                self.lbl_speed.config(text=f"Speed: {mbps} Mbps", fg="green")

                self.log(f"[SUCCESS] Bandwidth: {mbps} Mbps")

            else:

                self.lbl_speed.config(text="Fail", fg="red")

            self.test_running = False




        threading.Thread(target=task, daemon=True).start()




    def run_ping_test(self):

        if self.test_running: return

        target = "10.0.2.20"

        self.log(f"Test: Measuring latency to {target}...")

        self.test_running = True




        def task():

            # Запуск пинга в фоновом потоке, чтобы GUI не вис

            cmd = ["sudo", "ip", "netns", "exec", "analyzer_sender", "ping", target, "-c", "4"]

            res = subprocess.run(cmd, capture_output=True, text=True)

            self.log("-" * 20)

            self.log(res.stdout)




            if res.returncode == 0:

                self.log("[SUCCESS] Target is reachable.")

            else:

                self.log("[FAILED] No response from target.")

            self.test_running = False




        threading.Thread(target=task, daemon=True).start()




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
```


## Ход [54]

```
[debeeque@debeeque-wrtbwxx9 ~]$ arp -a

bash: arp: command not found

[debeeque@debeeque-wrtbwxx9 ~]$ man arp

[debeeque@debeeque-wrtbwxx9 ~]$ yay arp

300 aur/wol_qt 2.4-3 (+0 0.00) 

    Qt gui to ARP scan and send WakeOnLan packets

299 aur/harp 1.30-1 (+0 0.00) 

    Data harmonization toolset for scientific earth observation data

298 aur/manga-sharp 0.6.1-2 (+0 0.00) 

    CLI manga downloader and reader with lightweight web interface

297 aur/larp-fetch-git r1.0-1 (+0 0.00) 

    Neofetch-adjacent Python CLI powered by fastfetch with selectable ASCII logos

296 aur/fsharplint-bin 0.26.0-1 (+0 0.00) (Orphaned) 

    Lint tool for F#

295 aur/obs-time-warp-scan 0.1.7-1 (+0 0.00) 

    Time Warp Scan filter for OBS Studio

294 aur/karp 25.03.80-1 (+0 0.00) (Orphaned) 

    Simple PDF editor to arrange, merge and improve PDF file(s)

293 aur/vx68k-git 2.alpha.1.r15.gdba943d-1 (+0 0.00) 

    Virtual X68000 - emulator of Sharp X68000 implemented in C++

292 aur/r-similarpeak 1.42.0-1 (+0 0.00) 

    Metrics to estimate a level of similarity between two ChIP-Seq profiles

291 aur/omnisharp-vim-git r1779.d322a70-1 (+0 0.00) 

    Vim omnicompletion (intellisense) and more for C#.

290 aur/notify-sharp-3 3.0.3-4 (+0 0.00) (Orphaned) 

    C# D-Bus client library for desktop notifications (GTK+ 3 version)

289 aur/webkit2-sharp 2.10.9-3 (+0 0.00) (Orphaned) (Out-of-date: 2024-03-20) 

    C Sharp bindings for WebKit 2 with GTK+ 3

288 aur/ttf-workplace-gothic 0.3-1 (+0 0.00) 

    Semi-condensed sans font for user interfaces inspired by the OS/2 Warp system font

287 aur/cloudflare-warp-minimal-bin 2025.10.186.0-1 (+0 0.00) 

    Minimal Cloudflare WARP client

286 aur/mediawarp 0.2.3-1 (+0 0.00) 

    EmbyServer API Optimization: Optimize playback of Strm files, customize the front-end style, customize the allowed access to the client, embedded scripts, work with Alist to realize Emby playback of web resources, recommended to use with AutoFilm.

285 aur/sharp-mx-c55-9-ps 1.5-1 (+0 0.00) (Out-of-date: 2025-12-08) 

    PPD files for Sharp PostScript Printers(BP-40C26 to BP-70C45)

284 aur/perl-carp-assert 0.22-4 (+0 0.00) (Orphaned) 

    executable comments

283 aur/jetbrains-resharper-commandlinetools 2024.2.6-2 (+0 0.00) 

    JetBrains ReSharper Command Line Tools

282 aur/michaelas-harp-vst 1.0.0-1 (+0 0.00) (Orphaned) 

    Michaelas Celtic Harp (VST)

281 aur/python-ariarpc 0.0.2.1-1 (+0 0.00) 

    Python aria2 RPC call.

280 aur/starport-git nightly-1 (+0 0.00) 

    The all-in-one platform to build, launch and maintain any crypto application on a sovereign and secured blockchain

279 aur/excalibar-git 0.0.1-1 (+0 0.00) 

    sharp and shiny taskbar

278 aur/usque 1.4.2-1 (+0 0.00) 

    Open-source reimplementation of the Cloudflare WARP client's MASQUE protocol.

277 aur/python-tree-sitter-c-sharp 0.23.1-2 (+0 0.00) 

    C# grammar for tree-sitter

276 aur/mdxmini-git r19.eda5bca-6 (+0 0.00) 

    C library for Sharp X68000 MDX music files

275 aur/larpmodeactive 1.0-5 (+0 0.00) 

    Fake terminal process simulator

274 aur/splan-notify-git 1.0.3-1 (+0 0.00) 

    Easily get Notifications from the StarPlaner timetables

273 aur/ttf-workplace-sans 1.04-1 (+0 0.00) 

    Semi-condensed sans font for user interfaces inspired by the OS/2 Warp system font

272 aur/sparkleshare 3.38-1 (+0 0.00) (Orphaned) 

    Collaboration and sharing tool based on git written in C Sharp

271 aur/mediawarp-git 0.2.3.r15.gf7cad16-1 (+0 0.00) 

    EmbyServer API Optimization: Optimize playback of Strm files, customize the front-end style, customize the allowed access to the client, embedded scripts, work with Alist to realize Emby playback of web resources, recommended to use with AutoFilm.

270 aur/karpor-git 0.5.9.r2.g04f6467-1 (+0 0.00) (Orphaned) 

    Kubernetes visualization tool for developer and platform engineering teams

269 aur/ttf-workplace-console 1.00-1 (+0 0.00) 

    Monospaced font inspired by the OS/2 Warp System VIO

268 aur/karpor-bin 0.6.4-1 (+0 0.00) 

    Intelligence for Kubernetes. World's most promising Kubernetes Visualization Tool for Developer and Platform Engineering teams.(Written in Go,prebuilt version)

267 aur/warpforge-git r261.5be2023-1 (+0 0.00) 

    Putting things together. Consistently.

266 aur/flying-carpet 9.0.9-1 (+0 0.00) 

    File transfer between Android, iOS, Linux, macOS, and Windows over ad hoc WiFi

265 aur/perl-marpa-r2 12.000000-1 (+0 0.00) 

    Perl/CPAN Module Marpa::R2

264 aur/python-kaldilm-git 1.13-1 (+0 0.00) (Orphaned) 

    Python wrapper for arpa2fst from the kaldi speech toolkit.

263 aur/mdxplay-git r19.eda5bca-6 (+0 0.00) 

    Command line player for Sharp X68000 MDX music files

262 aur/json2sharp-bin 1.3.0.0-1 (+0 0.00) 

    CLI tool for converting JSON objects to class definitions

261 aur/tarp 0.0.2-1 (+0 0.00) 

    Fast and simple stream processing of files in tar files, useful for deep learning, big data, and many other applications.

260 aur/harper-git 1526.8578e2b-1 (+0 0.00) 

    The Grammar Checker for Developers

259 aur/warppulse 0.1.0-1 (+0 0.00) 

    The ultimate premium GUI for Cloudflare Warp on Linux.

258 aur/plogue-tablewarp2 1:1.980_beta1~6-1 (+0 0.00) (Out-of-date: 2025-07-16) 

    Plogue audio plugins, beta Linux port (unofficial support, DO NOT report bugs upstream!)

257 aur/vitott-git r50.fa5f455-1 (+0 0.00) 

    Multiband compressor from famous spectral warping synthesizer

256 aur/ros-noetic-cpr-onav-description 0.1.9-1 (+0 0.00) 

    ROS - Clearpath OutdoorNav URDF description

255 aur/bg-plugins.lv2-git r101.5fefe42-1 (+0 0.00) 

    CV arpeggiator and MIDI-pattern plugin developed for the MOD platform by Bram Geisen

254 aur/gohpts 1.12.4-1 (+0 0.00) 

    Simple CLI tool to transform SOCKS proxy into HTTP proxy with IPv4/IPv6 support for TCP/UDP Transparent Proxy (Redirect and TProxy), Proxychains, ARP/NDP/RA/RDNSS spoofing and Traffic Sniffing

253 aur/pdfsharpen-git 0.1.0.r2.g41b0705-1 (+0 0.00) 

    Sharpen scanned PDFs by rasterizing pages and applying an unsharp mask

252 aur/go-carpet 1.10.0-3 (+0 0.00) 

    Tool for show test coverage in terminal for Go source files

251 aur/flying-carpet-git 8.0.2.r1.gc1ace97-1 (+0 0.00) 

    File transfer between Android, iOS, Linux, macOS, and Windows over ad hoc WiFi

250 aur/sharps-talking-clock 1-1 (+0 0.00) 

    CLI version of the old Sharps talking clock

249 aur/nono 1.7.0-1 (+0 0.00) 

    Omron LUNA-I/LUNA-88K, Sharp X68030, and NEWS NWS-1750 emulator

248 aur/microserver 0.2.1-2 (+0 0.00) 

    Simple ad-hoc server with SPA support based on Warp!. Excellent for testing React, Angular, Vue apps and the like.

247 aur/warp-svc-runit 1.0.0-1 (+0 0.00) 

    runit service for Cloudflare WARP daemon (warp-svc)

246 aur/turbowarp-desktop-git 1.15.3.r0.gbfb4c15-1 (+0 0.00) 

    Scratch mod with a compiler to run projects faster, dark mode for your eyes, a bunch of addons to improve the editor, and more.(Use system-wide electron)

245 aur/warp-terminal-autoup-bin 0.2026.03.25.08.24.stable_05-1 (+0 0.00) 

    Warp, the Rust-based terminal for developers and teams

244 aur/carp 0.8.2-7 (+0 0.00) 

    EncFS gui and cli front-end

243 aur/karpor 0.6.4-1 (+0 0.00) 

    Kubernetes visualization tool for developer and platform engineering teams

242 aur/tpsrelw 1.74-1 (+0 0.00) 

    Relative warps analysis

241 aur/carpd-git r1.7aac36c-1 (+0 0.00) (Orphaned) 

    Small tool that prints a count of total pending updates for Arch

240 aur/libretro-xmil-git r286.6a52dc2-1 (+0 0.00) 

    Sharp X1 core for libretro

239 aur/forge-server-waystones 11.1.0-2 (+0 0.00) (Orphaned) 

    This mod adds waystone blocks that the player can return to once they've been activated, either through a Warp Scroll, a rechargeable Warp Stone, or by using an existing waystone to hop from one to the other.

238 aur/nvim-yarp-git r59.bb5f5e0-2 (+0 0.00) 

    (an) attempt (at) writing a remote plugin framework without :UpdateRemotePlugins.

237 aur/yarpgen v1.1.272.g700f5a2-1 (+0 0.00) 

    (Yet Another Random Program Generator) for stress testing compilers

236 aur/fsharp-mono-bin 5.0.0.0-1 (+0 0.00) 

    The legacy Mono F# Compiler, Core Library & Tools (Xamarin binary build). Newer versions are included in dotnet-core.

235 aur/spigot-plugin-essentialsx 2.19.4-1 (+0 0.00) (Orphaned) 

    EssentialsX offers 130 commands useful on just about every server, initial kits, mob spawning, economy, warps along the map, houses, etc.

234 aur/fsharp-language-server 0.1.27-1 (+0 0.00) (Orphaned) (Out-of-date: 2023-06-20) 

    Language server for F#, utilizing the Language Server Protocol

233 aur/pixelitor 4.3.1-1 (+0 0.00) 

    Advanced image editor with support for layers, layer masks, text layers, multiple undo, blending modes, cropping, Gaussian blurring, unsharp masking, histograms, etc.

232 aur/gtk-theme-e17gtk-revolved-git 2217140-1 (+0 0.00) 

    A dark GTK2/GTK3 theme with sharp corners, which is designed for use in Enlightenment and gives the elegant look of Enlightenment to GTK widgets - Revolved version.

231 aur/opsec-shield 1.0.0-1 (+0 0.00) (Orphaned) 

    Privacy and security toolkit with Cloudflare WARP VPN integration, Java malware scanner, password fortifier, and metadata anonymizer

230 aur/warp-packer 0.4.5.1-1 (+0 0.00) 

    Create self-contained single binary applications making it sipmler and more ergonomic to deliver your application to your customers

229 aur/r-ncgtw 1.22.0-1 (+0 0.00) 

    Alignment of LC-MS Profiles by Neighbor-wise Compound-specific Graphical Time Warping with Misalignment Detection

228 aur/csharp-language-server 5.4.0_2.26060.1-1 (+0 0.00) 

    A wrapper around Roslyn language server which makes compatible with editors other than VSCode

227 aur/nethole 2.0-1 (+0 0.00) 

    A wifi tool which uses arpspoof to exploit WPA3 and deauthenticate it regardless of its MFP

226 aur/python-dearpygui 2.2.0-1 (+0 0.00) 

    A fast and powerful Graphical User Interface Toolkit for Python with minimal dependencies

225 aur/keysharp-git r1895.55b0ffa-1 (+0 0.00) 

    Cross-platform rewrite of AutoHotkey in C#. Fork of now-defunct IronAHK. X11 version.

224 aur/ttf-arphic-tex-extra 20161212-1 (+0 0.00) 

    TrueType versions of the Chinese Arphic fonts for use with XeLaTeX and LuaLaTeX.

223 aur/qmidiarp-git 0.6.5.r20.gd774efc-1 (+0 0.00) 

    A MIDI arpeggiator, phrase generator and controller LFO for the ALSA sequencer.

222 aur/clangsharp-pinvoke-generator 21.1.8.2-2 (+0 0.00) 

    A tool that takes a C/C++ header files as input and generates C# interop code

221 aur/fcitx5-inflex-themes-git r4.86d0a36-2 (+0 0.00) 

    An aesthetic, modern fcitx5 theme featuring sharp-edged rectangle design.

220 aur/cloudflare-warp-panel 8.1.0-2 (+0 0.00) 

    A graphical control panel (GUI) for the Cloudflare WARP client for Linux.

219 aur/sharp-craft-launcher-bin 1.2.0-2 (+0 0.00) 

    A super light, fast, clean minecraft launcher framework written in rust.

218 aur/marsdev-git r160.908caa4-1 (+0 0.00) 

    Cross-platform Sega Mega Drive / Super 32X / Sharp X68000 toolchain

217 aur/0xmew-toolkit 3.6-2 (+0 0.00) 

    Advanced Network Attack Toolkit by 0xMew (ARP Spoof, Kill, SNI Spy)

216 aur/carp-git v0.3.0.r198.g6954642c-1 (+0 0.00) (Orphaned) (Out-of-date: 2024-06-23) 

    A statically typed lisp, without a GC, for real-time applications.

215 aur/wgcf-cli 0.3.6-1 (+0 0.00) 

    A command-line tool for Cloudflare-WARP API, built using Cobra.

214 aur/wgcf-cli-bin 0.3.6-1 (+0 0.00) 

    A command-line tool for Cloudflare-WARP API, built using Cobra

213 aur/mod-arpeggiator-lv2-git r117.82f3d9f-1 (+0 0.00) 

    A MIDI arpeggiator LV2 plugin from MOD Devices (git version)

212 aur/torch7-warp-ctc v1.0.r32.gbc29dcf-1 (+0 0.00) (Orphaned) 

    A fast parallel implementation of CTC, on both CPU and GPU.

211 aur/farpdf-git v0.1.r29.g15cc8d7-1 (+0 0.00) 

    A experimental PDF software designed for serious readers.

210 aur/ken 1.1.1-1 (+0 0.00) 

    A sharp AUR/Pacman helper written in Go. Stable version.

209 aur/ken-bin 1.1.1-1 (+0 0.00) 

    A sharp AUR/Pacman helper. Pre-compiled binary version.

208 aur/python-hopcroftkarp-git r45.2846e1d-1 (+0 0.00) 

    a module to find a maximum matching in bipartite graphs

207 aur/ken-git r15.5582b6d.hahalol-1 (+0 0.00) 

    A sharp AUR/Pacman helper written in Go. Git version.

206 aur/solidarp-git v0.3.0.r0.g7ab516f-1 (+0 0.00) 

    A stable random arpeggiator VST3 plugin (git version)

205 aur/perl-carp-object 1.02-1 (+0 0.00) 

    a replacement for Carp or Carp::Clan, object-oriented

204 aur/planetarysystemstacker-git 0.8.31-1 (+0 0.00) (Orphaned) 

    Produce a sharp image of a planetary system object

203 aur/burnoutsharp-bin 3.5.0-1 (+0 0.00) 

    Protection, packer, and archive scanning library

202 aur/gtk-theme-razor-sharp r11.da5ccb8-1 (+0 0.00) 

    A Amazing GTK3/4 red theme made by NillyTheL0L

201 aur/starpsx-bin 0.6.4-1 (+0 0.00) 

    A WIP PlayStation 1 emulator written in Rust

200 aur/python-hopcroftkarp 1.2.5-1 (+0 0.00) 

    Implementation of Hopcroftkarp's algorithm

199 aur/parpd-git 1.7.r17.ga2cadd4-1 (+0 0.00) 

    A RFC 1027 compliant proxy ARP daemon

198 aur/csharpier-bin 1.1.2-1 (+0 0.00) (Orphaned) 

    An opinionated code formatter for C#

197 aur/starpls 0.1.22-1 (+0 0.00) 

    An LSP implementation for Starlark

196 aur/warpdl 1.0.4-1 (+0 0.00) 

    A powerful and versatile cross-platform download manager.

195 aur/smlsharp-graphics 0.1.1-1 (+0 0.00) 

    A graphics library for SML#.

194 aur/libretro-px68k-git 388.b309941-1 (+1 0.00) 

    Portable SHARP X68000 Emulator for PSP, Android and other platforms

193 aur/warpinator-git 2.0.1.r0.gbac599ca-1 (+1 0.00) 

    Share files across the LAN

192 aur/libmarpa 8.6.2-2 (+1 0.00) 

    Marpa parse engine C library

191 aur/r-rarpack 0.11.0-4 (+1 0.00) 

    Solvers for Large Scale Eigenvalue and SVD Problems

190 aur/csharp-ls 0.22.0-1 (+1 0.03) 

    Roslyn-based LSP language server for C#

189 aur/kickthemout-git 0.1.r153.g9238b1b-1 (+1 0.00) (Orphaned) 

    Kick devices off your network by performing an ARP Spoof attack.

188 aur/dbus-sharp 0.8.1-4 (+1 0.00) (Orphaned) 

    C# implementation of D-Bus

187 aur/r-dtw 1.23.1-3 (+1 0.08) 

    Dynamic Time Warping Algorithms

186 aur/python-arpreq 0.3.3-4 (+1 0.00) 

    Python C extension to query the Kernel ARP cache for the MAC address of a given IP address.

185 aur/sharp-mx-3050to6170-ps 1.0-1 (+1 0.00) (Orphaned) (Out-of-date: 2024-05-15) 

    PPD files for Sharp PostScript Printers(MX-3050N to MX-6170FN)

184 aur/mingw-w64-arpack 3.9.1-1 (+1 0.00) 

    Fortran77 subroutines designed to solve large scale eigenvalue problems (mingw-w64)

183 aur/python-dtw-python-git 1.3.0-1 (+1 0.00) (Orphaned) 

    Python port of R's Comprehensive Dynamic Time Warp algorithm package

182 aur/dbus-sharp-glib 0.6.0-4 (+1 0.00) (Orphaned) 

    C# GLib implementation of D-Bus

181 aur/sharp-mx-182to232d-ps 1.1-1 (+1 0.00) (Out-of-date: 2024-05-16) 

    PPD files for Sharp PostScript Printers(MX-182 to MX-232D)

180 aur/pearpass-bin 1.5.0-1 (+1 1.00) 

    PearPass is a distributed password manager powered by Pear Runtime. It allows secure storage of passwords, credit card details, and secure notes, with peer-to-peer syncing and end-to-end encryption.

179 aur/r-dtwclust 6.0.0-1 (+1 0.08) 

    Time series clustering along with optimized techniques related to the Dynamic Time Warping distance and its corresponding lower bounds.

178 aur/oblivion-desktop 3.11.0-1 (+1 0.00) 

    Unofficial Warp Client

177 aur/warp-cli 2025.8.779.0-1 (+1 0.05) 

    Cloudflare WARP Client for Arch Linux

176 aur/warp-git 0.8.1.r5.g18a64fe-1 (+1 0.00) 

    Fast and secure file transfer

175 aur/mhy-warp-bin 2.0.8-1 (+1 0.00) 

    米游抽卡记录查询软件

174 aur/glade-sharp 2.12.45-1 (+1 0.00) (Orphaned) 

    Glade bindings for C#

173 aur/epk2extract-git r709-1 (+1 0.00) 

    Extraction tool for LG, Hisense, Sharp, Philips/TPV, Thompson and similar TVs/Embedded Devices.

172 aur/udeler-bin 1.13.4-1 (+1 0.00) 

    Unofficail binary installer for heliomarpm's fork of udeler

171 aur/starpu 1.3.11-2 (+1 0.00) (Out-of-date: 2025-10-30) 

    Task programming library for hybrid architectures

170 aur/fparser-git r19.e625e26-2 (+1 0.00) 

    Function Parser for C++, Fork from http://warp.povusers.org/FunctionParser/

169 aur/om-sharp-bin 1.5-1 (+1 0.00) (Out-of-date: 2024-03-24) 

    Offshoot and inofficial successor to the OpenMusic composition software

168 aur/git-warp-time-git 0.4.3.r1.g690557a-2 (+1 0.00) 

    reset file timestamps to repo state

167 aur/polarproxy-bin 1.0.0-1 (+1 0.00) 

    Transparent TLS and SSL inspection proxy primarily designed for incident responders and malware researchers to intercept, decrypt, and re-encrypt TLS encrypted traffic from malware while saving it in a PCAP file.

166 aur/warpd-wayland-git r231.567205b-1 (+1 0.00) (Orphaned) (Out-of-date: 2024-04-01) 

    A small program which facilitates recursively warping the pointer to different quadrants on the screen (wayland build).

165 aur/barpyrus-git r118.671eb8d-1 (+0 0.00) 

    A python wrapper for lemonbar/conky

164 aur/tarpyt 25.01-1 (+0 0.00) 

    A Python ssh/http/smtp/etc. tarpit

163 aur/warp-plus 1.2.6-1 (+1 0.00) 

    An open-source implementation of Cloudflare's Warp, enhanced with Psiphon integration

162 aur/libedssharp-git r526.6f67539-1 (+1 0.00) 

    A CanOpen EDS editor and library in C# with CanOpenNode export for Object Dictionary

161 aur/skia-sharp-atl-git r67245.ced64f6f90-3 (+1 0.00) 

    A complete 2D graphic library for drawing Text, Geometries, and Images (Mis012 fork)

160 aur/libedssharp 0.8-1 (+1 0.00) 

    A CanOpen EDS editor and library in C# with CanOpenNode export for Object Dictionary

159 aur/mc-fabric-carpet-git 1.16.4.1.4.21.r2049.35715c93-1 (+1 0.00) 

    A mod for vanilla Minecraft that allows you to take full control of what matters

158 aur/parpd 2.1.1-1 (+0 0.00) 

    Proxy-ARP daemon

157 aur/warpd-wayland v1.3.5-1 (+1 0.00) 

    A modal keyboard driven interface for mouse manipulation.

156 aur/sharpcraftlauncher 1.2.0-2.0 (+1 0.00) 

    A very light, fast, simple, rust-made Minecraft launcher

155 aur/parpar-bin 0.4.5-1 (+1 0.00) 

    A high-performance, multithreaded PAR2 creation tool

154 aur/gimp-refocus 0.9.0-5 (+1 0.00) (Orphaned) 

    A sharpen plugin for gimp using FIR Wiener filtering

153 aur/omnisharp-roslyn-bundled 1.37.6-1 (+1 0.00) (Out-of-date: 2021-10-15) 

    LSP server for C# - version with bundled mono

152 aur/csharpier 1.2.6-1 (+1 0.49) 

    An opinionated code formatter for C#

151 aur/vapoursynth-plugin-awarp-git 2.0.gb3f2fc8-1 (+0 0.00) 

    Plugin for Vapoursynth: awarp (GIT version)

150 aur/yarp 3.3.3-1 (+2 0.00) (Orphaned) (Out-of-date: 2023-10-25) 

    Yet Another Robot Platform

149 aur/notify-sharp 0.4.1-3 (+2 0.00) 

    C Sharp D-Bus client library for desktop notifications

148 aur/ttf-arphic-extra 20190327-4 (+2 0.00) 

    Extra fonts released under revised Arphic Public License for non-profit use only

147 aur/sharp-mx-c26-ps 1.4-1 (+2 0.00) 

    PPD files for Sharp PostScript Printers(MX-C26)

146 aur/cloudflarewarpspeedtest-bin v1.5.15-1 (+2 0.03) 

    Test the latency and speed of all Cloudflare Warp IPs to obtain the lowest latency and port. ⭐WARP IP 优选工具

145 aur/omnisharp-roslyn-bin 1.39.15-1 (+2 0.00) 

    OmniSharp server (STDIO) based on Roslyn workspaces

144 aur/gkeyfile-sharp 0.1-4 (+2 0.00) 

    Mono bindings for GLib’s GKeyFile

143 aur/warpgui-bin 2.5-1 (+2 0.00) 

    GUI for Cloudflare ™ WARP.(Prebuilt Version)

142 aur/sharp-mx-283to503-ps 1.3-1 (+2 0.00) 

    PPD files for Sharp PostScript Printers(MX-283 to MX-503)

141 aur/swarp 0.1-4 (+2 0.00) 

    Simple pointer warp

140 aur/librearp-git r265.b0f7798-1 (+1 0.00) 

    A pattern-based arpeggio generator plugin

139 aur/warp-plus-git 1.2.5.r0.a49dbf1-2 (+2 0.00) 

    An open-source implementation of Cloudflare's Warp, enhanced with Psiphon integration (GitHub Version).

138 aur/skia-sharp-atl r67245.ced64f6f90-4 (+2 0.00) 

    A complete 2D graphic library for drawing Text, Geometries, and Images (Mis012 fork)

137 aur/tree-sitter-c-sharp-git 0.23.1.r21.g485f0ba-1 (+0 0.00) 

    C# grammar for tree-sitter

136 aur/qwarp 0.7.7-1 (+2 1.98) 

    A lightweight, Wayland-native Qt6 wrapper for cloudflare-warp-bin

135 aur/warp-gui 0.3.0-3 (+2 0.00) 

    A GUI application based on warp-cli for linux written in Rust

134 aur/vapoursynth-plugin-warpsharpsupport-git 1.0.g42f3b5e-1 (+1 0.00) 

    Plugin for Vapoursynth: warpsharpsupport (GIT version)

133 aur/vapoursynth-plugin-mcdegrainsharp-git r6.abdc093-1 (+1 0.00) 

    Plugin for Vapoursynth: mcdegrainsharp (GIT version)

132 aur/vapoursynth-plugin-sharpaamcmod-git r6.4241d37-1 (+1 0.00) 

    Plugin for Vapoursynth: sharpaamcmod (GIT version)

131 aur/vapoursynth-plugin-psharpen-git r6.bde0bd8-1 (+1 0.00) 

    Plugin for Vapoursynth: psharpen (GIT version)

130 aur/vapoursynth-plugin-minsharp-git 4.2.gf90c5a7-1 (+1 0.00) 

    Plugin for Vapoursynth: minsharp (GIT version)

129 aur/tree-sitter-c-sharp 0.23.1-4 (+0 0.00) 

    C# grammar for tree-sitter

128 aur/oblivion-desktop-git 3.11.0.r6.g9fdf217-2 (+3 0.21) 

    Unofficial Warp Client for Windows/Mac/Linux (GitHub Version)

127 aur/wgcf-git 2.2.15.r0.140f983-1 (+3 0.00) 

    Generate WireGuard profile from Cloudflare Warp account

126 aur/rime-solarpinyin 1.2.0.20220909-1 (+3 0.00) 

    Simplified pinyin input for rime

125 aur/vital-synth-vst-bin 1.5.5-5 (+3 0.01) 

    Spectral warping wavetable synth - VST plugin

124 aur/gio-sharp 0.3-3 (+3 0.00) 

    Mono bindings to Glib's libgio

123 aur/vital-synth-standalone-bin 1.5.5-5 (+3 0.01) 

    Spectral warping wavetable synth - standalone

122 aur/vital-synth-clap-bin 1.5.5-5 (+3 0.01) 

    Spectral warping wavetable synth - CLAP plugin

121 aur/vital-synth-vst3-bin 1.5.5-5 (+3 0.01) 

    Spectral warping wavetable synth - VST3 plugin

120 aur/karp-git r551.1415cae-1 (+3 0.10) 

    Simple UI for PDF files modification.

119 aur/r-warp 0.2.3-1 (+1 0.00) 

    Group Dates

118 aur/gnome-keyring-sharp 1.0.2-7 (+3 0.00) 

    A fully managed implementation of libgnome-keyring

117 aur/deltarpm 3.6.5-1 (+3 0.00) (Orphaned) 

    Create deltas between rpms

116 aur/cloudflare-warp-nox-bin 2026.1.150-1 (+4 0.70) 

    Cloudflare Warp Client (for servers without graphical environment)

115 aur/xedgewarp 1.1-1 (+4 0.00) 

    xedgewarp is a window manager agnostic tool for pointer warping between outputs

114 aur/gtk-theme-e17gtk-git V3.22.2.r1.gecebae2-2 (+4 0.00) 

    A dark GTK2/GTK3 theme with sharp corners, which is designed for use in Enlightenment and gives the elegant look of Enlightenment to GTK widgets.

113 aur/ttf-miracode 1.0-2 (+4 0.01) 

    A sharp, readable, vector-y version of Monocraft, the monospace programming font based on Minecraft.

112 aur/carps-cups-git r158.18d80d1-2 (+4 0.00) 

    CUPS driver for Canon CARPS printers

111 aur/ttf-medievalsharp 20200401-1 (+4 0.01) 

    A font based on gothic letters.

110 aur/flying-carpet-bin 9.0.9-1 (+5 0.00) 

    File transfer between Android, iOS, Linux, macOS, and Windows over ad hoc WiFi

109 aur/perl-carp-assert-more 2.9.0-1 (+5 0.00) 

    Convenience assertions for common situations

108 aur/vapoursynth-plugin-finesharp-git r14.892023c-1 (+3 0.00) 

    Plugin for Vapoursynth: finesharp (GIT Version)

107 aur/azaharplus-novulkan-git r10793.176135e9b-1 (+0 0.00) 

    AzaharPlus (Citra Fork) compiled without Vulkan support

106 aur/astraeditor-bin 1.1.4-1 (+1 0.57) 

    AstraEditor is a TurboWarp mod used to add more practical features to make your writing lightning fast.

105 aur/astraeditor-git 1.1.4-1 (+1 0.57) 

    AstraEditor is a TurboWarp mod used to add more practical features to make your writing lightning fast.

104 aur/grpc-csharp-plugin-bin 2.67.0-1 (+0 0.00) 

    Pre-compiled grpc_csharp_plugin binary extracted from Grpc.Tools NuGet package

103 aur/gtk-sharp-3-git 2.99.3.r76.gdadc19cf1-1 (+6 0.00) 

    C# bindings for GTK+ 3, built from sources.

102 aur/gnome-rdp 0.3.1.0-3 (+6 0.00) (Orphaned) 

    Remote desktop client for the GNOME Desktop with RDP/VNC/SSH capabilities, written in C Sharp

101 aur/cnrdrvcups-lb-bin 6.20.20-1 (+6 0.19) 

    CUPS Canon UFR II LIPSLX CARPS2 printer driver for LBP iR MF ImageCLASS ImageRUNNER Laser Shot i-SENSYS ImagePRESS ADVANCE printers and copiers

100 aur/autofilm-git 1.2.5.r34.g6aa94e0-1 (+0 0.00) 

    A small project to provide Strm direct-link playback for Emby and Jellyfin servers, recommended for use with MediaWarp.

99 aur/krathalans-endlessh-git r121.f063a48-3 (+3 0.00) 

    A tarpit to lock up SSH clients. Krathalan's fork

98 aur/warpd-git r238.6ece9f2-2 (+6 0.00) 

    A modal keyboard driven interface for mouse manipulation.

97 aur/addrwatch-git 1.0.1.r4.g3ac9f4e-4 (+1 0.00) 

    A tool similar to arpwatch for IPv4/IPv6 and ethernet address pairing monitoring

96 aur/turbowarp-desktop-bin 1.15.3-1 (+7 0.01) 

    Scratch mod with a compiler to run projects faster, dark mode for your eyes, a bunch of addons to improve the editor, and more.

95 aur/gnome-sharp 2.24.4-9 (+7 0.00) 

    GNOME bindings for C#

94 aur/gnome-vfs-sharp 2.24.4-9 (+7 0.00) 

    Mono bindings for GNOME-VFS

93 aur/libgnome-sharp 2.24.4-9 (+7 0.00) 

    Mono bindings for libgnome

92 aur/gconf-sharp-peditors 2.24.4-9 (+7 0.00) 

    Mono bindings for GConf - Property Editing classes

91 aur/gconf-sharp 2.24.4-9 (+7 0.00) 

    Mono bindings for GConf

90 aur/astromatic-swarp 2.41.5-1 (+3 0.00) 

    resamples and co-adds together FITS images using any arbitrary astrometric projection defined in the WCS standard.

89 aur/warp-plus-bin 1.2.6-1 (+7 0.01) 

    An open-source implementation of Cloudflare's Warp, enhanced with Psiphon integration.

88 aur/warpd v1.3.5-1 (+7 0.57) 

    A modal keyboard driven interface for mouse manipulation.

87 aur/smlsharp 4.2.0-1 (+7 0.00) 

    A new programming language in the Standard ML family

86 aur/marp-cli 4.3.1-1 (+7 0.87) 

    A CLI interface for Marp and Marpit based converters

85 aur/spigot-plugin-essentials 1:2.19.3-1 (+8 0.00) (Orphaned) (Out-of-date: 2023-06-13) 

    Essentials offers about 100 commands useful on just about every server, initial kits, mob spawning, economy, warps along the map, houses, etc.

84 aur/gtk-sharp-2 2.12.45-8 (+8 0.75) 

    GTK2 bindings for C#.

83 aur/autofilm 1.5.0_1-5 (+0 0.00) 

    A small project to provide Strm direct-link playback for Emby and Jellyfin servers, recommended for use with MediaWarp.

82 aur/vapoursynth-plugin-awarpsharp2-git 4.0.g886d4b7-1 (+6 0.00) 

    Plugin for Vapoursynth: awarpsharp2 (GIT version)

81 aur/acp6x-omen-dkms 1.0-2 (+0 0.00) 

    Patched AMD Yellow Carp Audio Driver for HP OMEN 16 (Fixes Board ID 15E2 Rev 62 AMD Microphone Array)

80 aur/abyss-engine-git r254.bf1feb3-1 (+4 0.00) 

    A game engine designed to run games similar to 2000's style ARPGs such as Diablo II

79 aur/oblivion-desktop-bin 3.11.0-0 (+10 0.01) 

    Unofficial Warp Client for Windows/Mac/Linux (Pre-compiled version)

78 aur/pixeluvo 1.6.0_2-1 (+11 0.00) 

    photo editor with crop, vignette, text, captions, resize, color correction, raw file, filter, warp, layers, mask, and more.

77 aur/warp-terminal-bin 0.2026.03.25.08.24.stable_01-1 (+11 1.35) 

    Warp is the intelligent terminal with AI and your dev team's knowledge built-in.

76 aur/sdrsharp 1.0.0.1457-5 (+11 0.02) 

    The most popular SDR program

75 aur/endlessh-git r100.dfe44eb-1 (+10 0.00) 

    A tarpit to lock up SSH clients

74 aur/addrwatch 1.0.2-1 (+3 0.65) 

    A tool similar to arpwatch for IPv4/IPv6 and ethernet address pairing monitoring

73 aur/azaharplus-appimage 2124_3_A-1 (+2 0.01) 

    A fork of the Azahar 3DS emulator that restores some features

72 aur/r-ptw 1.9.17-1 (+0 0.00) 

    Parametric Time Warping

71 aur/ahab-bin 0.3.5-1 (+1 0.43) 

    A Docker cleanup TUI - hunt down and harpoon unused Docker resources

70 aur/gimp-plugin-wavelet-sharpen 0.1.2-2 (+19 0.00) 

    Enhances apparent sharpness of an image by increasing contrast in high frequency space.

69 aur/armsimsharp 2.1-1 (+3 0.00) (Orphaned) (Out-of-date: 2024-05-22) 

    A desktop application for simulating the execution of ARM assembly language programs.

68 aur/omnisharp-roslyn 1.39.15-1 (+21 0.00) 

    OmniSharp server (STDIO) based on Roslyn workspaces

67 aur/apmw 1.0-4 (+0 0.00) 

    Apt-PacMan Warpper - 一个将apt风格命令转换为pacman命令的包装器

66 aur/marp-cli-bin 4.3.1-2 (+23 0.00) 

    A CLI interface for Marp and Marpit based converters

65 aur/arp-scan-git r304.af905ce-1 (+1 0.00) 

    The ARP Scanner

64 aur/arpreply-git r2.10e96ec-1 (+0 0.00) (Orphaned) 

    arpreply - A tool to respond to ARP requests

63 aur/arptables-git 0.0.5.r1.gc90e809-1 (+0 0.00) 

    ARP filtering utility

62 aur/vital-synth 1.5.5-14 (+28 0.15) 

    Spectral warping wavetable synth. Manual download of .deb installer required.

61 aur/arpack-git 3.9.1.r38.gf73592d-1 (+0 0.00) 

    Collection of Fortran77 subroutines designed to solve large scale eigenvalue problems

60 aur/cndrvcups-lb-bin 3.70-2 (+30 0.00) 

    CUPS Canon UFR II LT LIPSLX CARPS2 printer driver for imageCLASS D Laser Shot LBP i-SENSYS MF imagePRESS iPR imageRUNNER iR ADVANCE iR-ADV FAX color printers and copiers, does not require PCL/PXL or PS dealer LMS license

59 aur/flat-remix-gtk 20240730-1 (+38 0.10) 

    Flat Remix GTK theme is a pretty simple gtk window theme inspired on material design following a modern design using "flat" colors with high contrasts and sharp borders.

58 aur/art-sharp 2.24.4-9 (+7 0.00) 

    Mono bindings for libart

57 aur/cnrdrvcups-lb 1:6.20.1.20-1 (+38 0.50) 

    CUPS Canon UFR II LIPSLX CARPS2 printer driver for LBP iR MF ImageCLASS ImageRUNNER Laser Shot i-SENSYS ImagePRESS ADVANCE printers and copiers

56 aur/perl-net-arp 1.0.12-1 (+39 0.00) 

    Perl Module: Extension for creating ARP Packets

55 aur/arpchat-bin 1.0.0-2 (+0 0.00) 

    Answering the question nobody asked: what if you wanted to text your friends using only ARP?

54 aur/arpalert 2.0.12-1 (+0 0.00) (Orphaned) 

    Monitor ARP changes in ethernet networks

53 aur/arptables 0.0.4-6 (+0 0.00) (Orphaned) 

    ARP filtering utility

52 aur/cloudflare-warp-bin 2026.1.150-1 (+72 2.21) 

    Cloudflare Warp Client

51 aur/arpfox-git v1.0.0.rc1.r4.gabfe404-1 (+1 0.00) 

    An arpspoof alternative (written in Go) that injects spoofed ARP packets into a LAN.

50 aur/arpfox-bin 1.0.0-1 (+1 0.00) 

    An arpspoof alternative that injects spoofed ARP packets into a LAN.

49 aur/libsearpc 2:3.3.0-5 (+88 0.00) 

    A simple C language RPC framework (including both server side & client side)

48 aur/arping-th 2.25-1 (+6 0.00) 

    ARP Ping from Thomas Habets (aka Debian arping)

47 aur/arpackpp 2.4.0-1 (+5 0.01) 

    Arpack++ with patches (C++ interface to ARPACK)

46 aur/arpoison 0.7-1 (+10 0.00) (Orphaned) 

    The UNIX arp cache update utility

45 aur/arpfox 1.0.0-1 (+1 0.00) 

    An arpspoof alternative that injects spoofed ARP packets into a LAN.

44 aur/arpon-ng 3.0-4 (+5 0.00) (Out-of-date: 2019-03-01) 

    Prevents MITM attacks on the Address Resolution Protocol (ARP)

43 aur/arpage 0.3.3-11 (+13 0.00) 

    JACK MIDI arpeggiator with transport and tempo sync

42 aur/arpc 0.8-1 (+0 0.00) 

    GRPC-like RPC library that supports file descriptor passing by using Argdata

41 multilib/lib32-libwebp 1.6.0-1 (285.8 KiB 941.5 KiB) 

    WebP library (32-bit)

40 extra/python-arpy 2.3.0-6 (17.8 KiB 71.5 KiB) 

    Library for accessing ar files

39 extra/texlive-latexextra 2026.0-3 (37.1 MiB 113.0 MiB) [texlive] 

    TeX Live - LaTeX additional packages

38 extra/python-aiodiscover 2.7.1-2 (35.4 KiB 151.1 KiB) 

    Discover Hosts via ARP and PTR lookup

37 extra/mighttpd2 4.0.4-28 (212.9 KiB 1.4 MiB) 

    High performance web server on WAI/warp

36 extra/texlive-latexrecommended 2026.0-3 (2.3 MiB 16.9 MiB) [texlive] 

    TeX Live - LaTeX recommended packages

35 extra/ucarp 1.5.2-9 (26.1 KiB 68.4 KiB) 

    Userspace implementation of the CARP protocol

34 extra/haskell-scotty 0.22-206 (201.0 KiB 1.0 MiB) 

    Haskell web framework inspired by Ruby's Sinatra, using WAI and Warp

33 extra/warpinator 1.8.8-2 (355.0 KiB 1.5 MiB) 

    LAN file sender, send and receive files across the network

32 extra/gtk-sharp-3 3.22.2-2 (1.1 MiB 10.5 MiB) 

    C# bindings for GTK 3

31 extra/cargo-tarpaulin 0.35.2-2 (2.7 MiB 7.9 MiB) 

    Tool to analyse test coverage of cargo projects

30 extra/ttf-arphic-uming 0.2.20080216.2-3 (7.5 MiB 20.1 MiB) 

    CJK Unicode font Ming style

29 extra/haskell-warp-tls 3.4.9-194 (45.4 KiB 176.9 KiB) 

    HTTP over TLS support for Warp via the TLS package

28 extra/perl-carp-always 0.16-5 (6.6 KiB 6.3 KiB) 

    Warns and dies noisily with stack backtraces

27 extra/okularpart5 23.08.5-3 (1.1 MiB 4.1 MiB) 

    Qt5 Okular KPart

26 extra/ipguard 1.04-8 (18.1 KiB 40.8 KiB) 

    ipguard - arp<->ip relation checking tool

25 extra/python-arpeggio 2.0.3-2 (69.4 KiB 361.6 KiB) 

    Packrat parser interpreter

24 extra/texlive-langchinese 2026.0-3 (103.9 MiB 198.2 MiB) [texlive-lang] 

    TeX Live - Chinese

23 extra/python-harparser 0.4-13 (10.7 KiB 34.5 KiB) 

    Python HAR Parser Utility

22 extra/texlive-mathscience 2026.0-3 (3.9 MiB 20.3 MiB) [texlive] 

    TeX Live - Mathematics, natural sciences, computer science packages

21 extra/git-warp-time 1.0.0-2 (328.8 KiB 789.4 KiB) 

    reset timestamps of Git repository files to the time of the last modifying commit

20 extra/ttf-arphic-ukai 0.2.20080216.2-3 (7.8 MiB 16.4 MiB) 

    CJK Unicode font Kaiti style

19 extra/haskell-warp-quic 0.0.0-438 (16.9 KiB 40.0 KiB) 

    Warp based on QUIC

18 extra/wgcf 2.2.25-1 (3.5 MiB 10.5 MiB) 

    Generate WireGuard profile from Cloudflare Warp account

17 extra/warp 0.9.2-3 (3.6 MiB 14.7 MiB) [gnome-circle] 

    Securely send files to each other via the internet or local network by exchanging a word-based code

16 extra/harper 1.12.0-1 (20.5 MiB 107.2 MiB) 

    The Grammar Checker for Developers

15 extra/skia-sharp 2.88.9-1 (2.4 MiB 6.8 MiB) 

    The Skia 2D Graphics library from Google exposed to .NET languages and runtimes across the board

14 extra/haskell-hxt-charproperties 9.5.0.0-7 (871.4 KiB 6.4 MiB) 

    Character properties and classes for XML and Unicode

13 extra/libwebp 1.6.0-2 (331.7 KiB 1.0 MiB) (Installed)

    WebP image codec library

12 extra/qmidiarp-lv2 0.7.4-1 (141.2 KiB 596.0 KiB) [lv2-plugins pro-audio] 

    A MIDI arpeggiator, phrase generator and controller LFO for the ALSA sequencer. - LV2 plugin

11 extra/qmidiarp-standalone 0.7.4-1 (288.4 KiB 943.2 KiB) [pro-audio] 

    A MIDI arpeggiator, phrase generator and controller LFO for the ALSA sequencer. - standalone

10 extra/qmidiarp 0.7.4-1 (2.8 KiB 0.0 B) 

    A MIDI arpeggiator, phrase generator and controller LFO for the ALSA sequencer.

9 extra/perl-carp-clan 6.08-11 (9.8 KiB 15.4 KiB) 

    Report errors from perspective of caller of a "clan" of modules

8 extra/ruby-redcarpet 3.6.1-1 (70.2 KiB 195.7 KiB) 

    A fast, safe and extensible Markdown to (X)HTML parser

7 extra/haskell-warp 3.4.0-22 (274.3 KiB 1.3 MiB) (Installed)

    A fast, light-weight web server for WAI applications.

6 extra/arpwatch 3.9-1 (330.4 KiB 1.1 MiB) 

    Ethernet/FDDI station activity monitor

5 extra/arp-scan 1.10.0-4 (473.4 KiB 1.5 MiB) 

    A tool that uses ARP to discover and fingerprint IP hosts on the local network

4 extra/arpack 3.9.1-3 (178.2 KiB 616.8 KiB) 

    Fortran77 subroutines for solving large scale eigenvalue problems

3 extra/drpm 0.5.3-1 (150.7 KiB 783.4 KiB) 

    A small library for fetching information from deltarpm packages

2 core/perl 5.42.1-1 (20.4 MiB 70.1 MiB) (Installed)

    A highly capable, feature-rich programming language

1 core/iptables-nft 1:1.8.11-2 (417.7 KiB 2.3 MiB) (Installed)

    Linux kernel packet control tool (using nft interface)

==> Packages to install (eg: 1 2 3, 1-3 or ^4)

==>
```


## Ход [56]

```
[debeeque@debeeque-wrtbwxx9 ~]$ arp -a

_gateway (172.20.10.1) at 92:4c:c5:30:89:64 [ether] on wlan0

[debeeque@debeeque-wrtbwxx9 ~]$ ip a

1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group de

fault qlen 1000

   link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00

   inet 127.0.0.1/8 scope host lo

      valid_lft forever preferred_lft forever

   inet6 ::1/128 scope host noprefixroute  

      valid_lft forever preferred_lft forever

2: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP

group default qlen 1000

   link/ether 84:c5:a6:44:8d:0b brd ff:ff:ff:ff:ff:ff

   inet 172.20.10.7/28 brd 172.20.10.15 scope global dynamic noprefixroute

wlan0

      valid_lft 3204sec preferred_lft 3204sec

   inet6 2a00:102a:5077:bc57:b449:2b37:18d0:32a1/64 scope global noprefixro

ute  

      valid_lft forever preferred_lft forever

   inet6 fe80::b4ee:bf3a:f92b:6f08/64 scope link noprefixroute  

      valid_lft forever preferred_lft forever

[debeeque@debeeque-wrtbwxx9 ~]$

[debeeque@debeeque-wrtbwxx9 ~]$ ip neighbor  

172.20.10.1 dev wlan0 lladdr 92:4c:c5:30:89:64 REACHABLE  

fe80::904c:c5ff:fe30:8964 dev wlan0 lladdr 92:4c:c5:30:89:64 router REACHABL

E  

2a00:102a:5077:bc57:ec6c:caa0:99:1d89 dev wlan0 lladdr 92:4c:c5:30:89:64 rou

ter STALE  

[debeeque@debeeque-wrtbwxx9 ~]$
```


## Ход [57]

```
[debeeque@debeeque-wrtbwxx9 ~]$ ssh muk0015@172.20.10.8

The authenticity of host '172.20.10.8 (172.20.10.8)' can't be established.

ED25519 key fingerprint is: SHA256:n+ZdFPdGeFJBoQdTLEpTm9WrFJzhbiKJAJTbZgOTi

p4

This key is not known by any other names.

Are you sure you want to continue connecting (yes/no/[fingerprint])? yes

Warning: Permanently added '172.20.10.8' (ED25519) to the list of known host

s.

muk0015@172.20.10.8's password:  

Linux raspberrypi 6.12.47+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.12.47-1+rpt1

(2025-09-16) aarch64




The programs included with the Debian GNU/Linux system are free software;

the exact distribution terms for each program are described in the

individual files in /usr/share/doc/*/copyright.




Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent

permitted by applicable law.

Last login: Mon Mar  2 17:13:31 2026 from 2a00:102a:404b:9c68:2c45:e54:fa52:

e7fd

muk0015@raspberrypi:~$ ip a

1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group de

fault qlen 1000

   link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00

   inet 127.0.0.1/8 scope host lo

      valid_lft forever preferred_lft forever

   inet6 ::1/128 scope host noprefixroute  

      valid_lft forever preferred_lft forever

2: eth0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc fq_codel state D

OWN group default qlen 1000

   link/ether b8:27:eb:ce:4e:16 brd ff:ff:ff:ff:ff:ff

3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP

group default qlen 1000

   link/ether b8:27:eb:9b:1b:43 brd ff:ff:ff:ff:ff:ff

   inet 172.20.10.8/28 brd 172.20.10.15 scope global dynamic noprefixroute

wlan0

      valid_lft 3018sec preferred_lft 3018sec

   inet6 2a00:102a:5077:bc57:66ad:cc9:42d3:d185/64 scope global noprefixrou

te  

      valid_lft forever preferred_lft forever

   inet6 fe80::9852:730d:de80:7ee9/64 scope link noprefixroute  

      valid_lft forever preferred_lft forever

muk0015@raspberrypi:~$ ip a

1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group de

fault qlen 1000

   link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00

   inet 127.0.0.1/8 scope host lo

      valid_lft forever preferred_lft forever

   inet6 ::1/128 scope host noprefixroute  

      valid_lft forever preferred_lft forever

2: eth0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc fq_codel state D

OWN group default qlen 1000

   link/ether b8:27:eb:ce:4e:16 brd ff:ff:ff:ff:ff:ff

3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP

group default qlen 1000

   link/ether b8:27:eb:9b:1b:43 brd ff:ff:ff:ff:ff:ff

   inet 172.20.10.8/28 brd 172.20.10.15 scope global dynamic noprefixroute

wlan0

      valid_lft 2961sec preferred_lft 2961sec

   inet6 2a00:102a:5077:bc57:66ad:cc9:42d3:d185/64 scope global noprefixrou

te  

      valid_lft forever preferred_lft forever

   inet6 fe80::9852:730d:de80:7ee9/64 scope link noprefixroute  

      valid_lft forever preferred_lft forever

как так получилось?
```


## Ход [66]

```
muk0015@raspberrypi:~/diploma_project$ ls

arp_scan.py  capture.pcap  gui_app.py  setup_network.sh

muk0015@raspberrypi:~/diploma_project$ cat gui_app.py  

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




       # Ряд 0: Основные функции

       tk.Button(btn_frame, text="1. SETUP NET", bg="#4CAF50", fg="white", c

ommand=self.run_setup, **btn_cfg).grid(row=0, column=0, padx=5, pady=2)

       tk.Button(btn_frame, text="2. ARP SCAN", bg="#2196F3", fg="white", co

mmand=self.run_arp_scan, **btn_cfg).grid(row=0, column=1, padx=5, pady=2)

       self.btn_monitor = tk.Button(btn_frame, text="3. LIVE STATS", bg="#60

7D8B", fg="white", command=self.toggle_monitoring, **btn_cfg)

       self.btn_monitor.grid(row=0, column=2, padx=5, pady=2)

       tk.Button(btn_frame, text="EXIT", bg="#f44336", fg="white", command=s

elf.close_app, **btn_cfg).grid(row=0, column=3, padx=5, pady=2)




       # Ряд 1: Тесты IPv4 и IPv6

       tk.Button(btn_frame, text="SPEED v4", bg="#9C27B0", fg="white", comma

nd=self.run_iperf_v4, **btn_cfg).grid(row=1, column=0, padx=5, pady=2)

       tk.Button(btn_frame, text="PING v4", bg="#FF5722", fg="white", comman

d=self.run_ping_v4, **btn_cfg).grid(row=1, column=1, padx=5, pady=2)

       tk.Button(btn_frame, text="SPEED v6", bg="#6A1B9A", fg="white", comma

nd=self.run_iperf_v6, **btn_cfg).grid(row=1, column=2, padx=5, pady=2)

       tk.Button(btn_frame, text="PING v6", bg="#E64A19", fg="white", comman

d=self.run_ping_v6, **btn_cfg).grid(row=1, column=3, padx=5, pady=2)




       self.res_frame = tk.LabelFrame(self.root, text=" Intelligence Dashboa

rd ", font=('Arial', 12, 'bold'), fg="darkblue")

       self.res_frame.pack(fill=tk.X, padx=10, pady=5)




       self.lbl_speed = tk.Label(self.res_frame, text="Speed: -- Mbps", font

=('Arial', 14, 'bold'))

       self.lbl_speed.pack(side=tk.LEFT, padx=20)

       self.lbl_icmp = tk.Label(self.res_frame, text="Live ICMP/6: 0", font=

('Arial', 14), fg="red")

       self.lbl_icmp.pack(side=tk.LEFT, padx=20)




       self.log_area = scrolledtext.ScrolledText(self.root, width=90, height

=12, font=('Consolas', 10))

       self.log_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)




   def log(self, text):

       self.log_area.insert(tk.END, f"{text}\n")

       self.log_area.see(tk.END)




   def run_setup(self):

       self.log("System: Refreshing network namespaces (IPv4 & IPv6)...")

       subprocess.run(["sudo", "./setup_network.sh"])

       self.log("[OK] Netns ready.")




   def execute_iperf(self, target, proto_name):

       if self.test_running: return

       self.log(f"Test: Running throughput test to {target} ({proto_name})..

.")

       self.lbl_speed.config(text="Testing...", fg="orange")

       self.test_running = True




       def task():

           cmd = ["sudo", "ip", "netns", "exec", "analyzer_sender", "iperf3"

, "-c", target, "-t", "5"]

           res = subprocess.run(cmd, capture_output=True, text=True)

           self.log(res.stdout)




           match = re.findall(r"([\d\.]+)\s+Mbits/sec\s+receiver", res.stdou

t)

           if not match: match = re.findall(r"([\d\.]+)\s+Mbits/sec", res.st

dout)




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

           cmd = ["sudo", "ip", "netns", "exec", "analyzer_sender", ping_cmd

, target, "-c", "4"]

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

       cmd = ["sudo", "ip", "netns", "exec", "analyzer_sender", "python3", "

arp_scan.py"]

       res = subprocess.run(cmd, capture_output=True, text=True)

       self.log(res.stdout)




   def toggle_monitoring(self):

       if not self.is_monitoring:

           self.is_monitoring = True

           self.btn_monitor.config(text="STOP STATS", bg="#FF9800")

           self.log("Monitor: Passive capture on eth1 (IPv4/v6)...")

           self.stats = {"TCP": 0, "UDP": 0, "ICMP": 0}

           threading.Thread(target=self.packet_sniff_thread, daemon=True).st

art()

           self.update_labels()

       else:

           self.is_monitoring = False

           self.btn_monitor.config(text="3. LIVE STATS", bg="#607D8B")

           if self.sniff_process: self.sniff_process.terminate()




   def packet_sniff_thread(self):

       cmd = ["sudo", "ip", "netns", "exec", "analyzer_monitor", "tcpdump",

"-i", "eth1", "-n", "-l"]

       try:

           self.sniff_process = subprocess.Popen(cmd, stdout=subprocess.PIPE

, stderr=subprocess.DEVNULL, text=True)

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

muk0015@raspberrypi:~/diploma_project$
```


## Ход [68]

```
я обновил toggle_keyboard в коде так как ты и сказал, но теперь network analyzer просто не запускается: muk0015@raspberrypi:~/diploma_project$ cat gui_app.py 

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

        # --- БЛОК 1: Основные кнопки ---

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




        # --- БЛОК 2: Security & Recon (NMAP) ---

        sec_frame = tk.LabelFrame(self.root, text=" Security & Recon (Nmap) ", font=('Arial', 10, 'bold'), fg="darkred")

        sec_frame.pack(fill=tk.X, padx=10, pady=2)




        tk.Label(sec_frame, text="Target IP:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)

        self.ip_entry = tk.Entry(sec_frame, font=('Arial', 11), width=15)

        self.ip_entry.insert(0, "10.0.2.20")

        self.ip_entry.pack(side=tk.LEFT, padx=5)




        self.scan_mode = tk.StringVar(value="LAN")

        tk.Radiobutton(sec_frame, text="LAN (Netns)", variable=self.scan_mode, value="LAN", font=('Arial', 9)).pack(side=tk.LEFT, padx=2)

        tk.Radiobutton(sec_frame, text="Wi-Fi (wlan0)", variable=self.scan_mode, value="WIFI", font=('Arial', 9)).pack(side=tk.LEFT, padx=2)




        tk.Button(sec_frame, text="START SCAN", bg="#333333", fg="white", font=('Arial', 9, 'bold'), command=self.run_nmap).pack(side=tk.LEFT, padx=10)

        

        # Кнопка виртуальной клавиатуры

        tk.Button(sec_frame, text="⌨ KBD", bg="#009688", fg="white", font=('Arial', 9, 'bold'), command=self.toggle_keyboard).pack(side=tk.RIGHT, padx=5)




        # --- БЛОК 3: Дашборд и Логи ---

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




   def toggle_keyboard(self):

        try:

            res = subprocess.run(["pidof", "matchbox-keyboard"], capture_output=True, text=True)

            if res.stdout.strip():

                subprocess.run(["killall", "matchbox-keyboard"])

                self.log("Keyboard: Closed.")

            else:

                # Запуск в нижней части экрана (x=0, y=280, ширина=800, высота=200)

                # Параметры зависят от разрешения твоего экрана

                subprocess.Popen(["matchbox-keyboard", "geometry", "800x200+0+280"])

                self.log("Keyboard: Opened at bottom.")

        except Exception as e:

            self.log(f"Keyboard Error: {e}")




    def run_nmap(self):

        if self.test_running: return

        target = self.ip_entry.get().strip()

        if not target:

            self.log("Error: Please enter a target IP.")

            return




        mode = self.scan_mode.get()

        self.test_running = True

        self.log(f"Recon: Starting Nmap scan against {target} via {mode}...")




        def task():

            # -F: Быстрый скан (топ порты), -sV: Определение версий

            if mode == "LAN":

                cmd = ["sudo", "ip", "netns", "exec", "analyzer_sender", "nmap", "-F", "-sV", target]

            else:

                cmd = ["sudo", "nmap", "-F", "-sV", target]




            res = subprocess.run(cmd, capture_output=True, text=True)

            self.log("-" * 30)

            self.log(f"NMAP RESULTS ({mode}):")

            self.log(res.stdout)

            self.log("-" * 30)

            self.test_running = False




        threading.Thread(target=task, daemon=True).start()




    # --- СТАРЫЕ ФУНКЦИИ (БЕЗ ИЗМЕНЕНИЙ) ---

    def run_setup(self):

        self.log("System: Refreshing network namespaces (IPv4 & IPv6)...")

        subprocess.run(["sudo", "./setup_network.sh"])

        self.log("[OK] Netns ready.")




    def execute_iperf(self, target, proto_name):

        if self.test_running: return

        self.log(f"Test: Running throughput test to {target} ({proto_name})...")

        self.lbl_speed.config(text="Testing...", fg="orange")

        self.test_running = True




        def task():

            cmd = ["sudo", "ip", "netns", "exec", "analyzer_sender", "iperf3", "-c", target, "-t", "5"]

            res = subprocess.run(cmd, capture_output=True, text=True)

            self.log(res.stdout)




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

            cmd = ["sudo", "ip", "netns", "exec", "analyzer_sender", ping_cmd, target, "-c", "4"]

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

        subprocess.run(["killall", "matchbox-keyboard"], stderr=subprocess.DEVNULL)

        self.root.destroy()

        sys.exit()




if __name__ == "__main__":

    root = tk.Tk()

    app = AnalyzerApp(root)

    root.mainloop()

muk0015@raspberrypi:~/diploma_project$ 

обнови весь код сам чтобы мне оставалось его лишь вставить целиком новый
```


## Ход [72]

```
что ж я решил пока выполнить все что связано со взаимодействием самого устройства я его включил и подключился по ssh и вот что есть и имеется: muk0015@raspberrypi:~$ ls

captures  Desktop  diploma_project  Documents  Downloads  generator.py  LCD-show  Music  network_logs  Pictures  Public  scapy_project  Templates  Videos

muk0015@raspberrypi:~$ cd diploma_project/

muk0015@raspberrypi:~/diploma_project$ ls

arp_scan.py  capture.pcap  gui_app.py  setup_network.sh

muk0015@raspberrypi:~/diploma_project$ cat arp_scan.py  

from scapy.all import *

# Настройки

iface = "eth2"

ip_range = "10.0.2.0/24"

print(f"Scanning {ip_range} on {iface}...")

try:

   ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_range),

                    iface=iface, timeout=2, verbose=False)

   print(f"Found {len(ans)} devices:")

   for sent, received in ans:

       print(f"IP: {received.psrc}  MAC: {received.hwsrc}")

except Exception as e:

   print(f"Error: {e}")

muk0015@raspberrypi:~/diploma_project$ cat capture.pcap  

�ò�QJi

�JJ�Lh�L8(E<u���







M&5abcdefghijklmnopqrstuvwabcdefghiQJir�**��������Lh







QJix�<<�Lh�L8�L8(E

�Lh




QJi��JJ�L8(E�LE<M�@�







U&5abcdefghijklmnopqrstuvwabcdefghiRJi�JJ�Lh�L8(E<u���







M%6abcdefghijklmnopqrstuvwabcdefghiRJi5JJ�L8(E�LE<M�@�







U%6abcdefghijklmnopqrstuvwabcdefghiSJi�3JJ�Lh�L8(E<u���







M$7abcdefghijklmnopqrstuvwabcdefghiSJi�3JJ�L8(E�LE<M�@�







U$7abcdefghijklmnopqrstuvwabcdefghiTJi��JJ�Lh�L8(E<u���







M#8abcdefghijklmnopqrstuvwabcdefghiTJi+�JJ�L8(E�LE<N=@g







U#8abcdefghijklmnopqrstuvwabcdefghiUJi�BJJ�Lh�L8(E<u���







M"9abcdefghijklmnopqrstuvwabcdefghiUJi@CJJ�L8(E�LE<N�@$







<<�Lh�L8�L8(EklmnopqrstuvwabcdefghiUJi�Y

�Lh




**�L8(E��Lh




�L8(E

VJimuk0015@raspberrypi:~/diploma_project$ cat gui_app.py  

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




       # --- БЛОК Security & Recon (NMAP) ---

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

        

       # Наша новая кнопка вызова кастомного Numpad

       tk.Button(sec_frame, text="⌨ NUMPAD", bg="#009688", fg="white", font=('Arial', 9, 'bold'), command=self.toggle_numpad).pack(side=tk.RIGHT, padx=5)




       # --- Дашборд ---

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




   # --- КАСТОМНАЯ КЛАВИАТУРА NUMPAD ---

   def toggle_numpad(self):

       if hasattr(self, 'numpad') and self.numpad.winfo_exists():

           self.numpad.destroy()

           return




       self.numpad = tk.Toplevel(self.root)

       self.numpad.title("IP Numpad")

       # Позиционируем в правой части экрана, чтобы не перекрывать логи

       self.numpad.geometry("240x300+540+150")

       self.numpad.attributes('-topmost', True)

       self.numpad.configure(bg="#ECEFF1")




       keys = [

           '7', '8', '9',

           '4', '5', '6',

           '1', '2', '3',

           '0', '.', 'DEL'

       ]




       row_idx, col_idx = 0, 0

       for key in keys:

           action = lambda x=key: self.numpad_press(x)

           btn = tk.Button(self.numpad, text=key, font=('Arial', 16, 'bold'), command=action, height=2, width=4)

           btn.grid(row=row_idx, column=col_idx, padx=5, pady=5)

           col_idx += 1

           if col_idx > 2:

               col_idx = 0

               row_idx += 1




       tk.Button(self.numpad, text="CLEAR", font=('Arial', 12, 'bold'), bg="#f44336", fg="white", command=lambda: self.ip_entry.delete(0, tk.END), height=2)

.grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="we")

       tk.Button(self.numpad, text="OK", font=('Arial', 12, 'bold'), bg="#4CAF50", fg="white", command=self.numpad.destroy, height=2).grid(row=row_idx, colu

mn=2, padx=5, pady=5, sticky="we")




   def numpad_press(self, key):

       if key == 'DEL':

           current = self.ip_entry.get()

           self.ip_entry.delete(0, tk.END)

           self.ip_entry.insert(0, current[:-1])

       else:

           self.ip_entry.insert(tk.END, key)

   # -----------------------------------




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

           # Добавлены агрессивные флаги: -T4 (быстро), --max-retries 1, --host-timeout 30s

           base_nmap = ["nmap", "-F", "-sV", "-T4", "--max-retries", "1", "--host-timeout", "30s", target]

            

           if mode == "LAN":

               cmd = ["sudo", "ip", "netns", "exec", "analyzer_sender"] + base_nmap

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

           cmd = ["sudo", "ip", "netns", "exec", "analyzer_sender", "iperf3", "-c", target, "-t", "5"]

           res = subprocess.run(cmd, capture_output=True, text=True)

            

           # Логируем возможные ошибки iperf3 (например, connection refused)

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

           cmd = ["sudo", "ip", "netns", "exec", "analyzer_sender", ping_cmd, target, "-c", "4"]

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

muk0015@raspberrypi:~/diploma_project$ cat setup_network.sh  

#!/bin/bash




# Очистка

killall dnsmasq 2>/dev/null

ip netns delete analyzer_monitor 2>/dev/null

ip netns delete analyzer_sender 2>/dev/null




# Создание пространств

ip netns add analyzer_monitor

ip netns add analyzer_sender




# Перемещение интерфейсов

ip link set dev eth1 netns analyzer_monitor

ip link set dev eth2 netns analyzer_sender




# ==========================================

# Настройка Monitor (eth1)

# ==========================================

ip netns exec analyzer_monitor ip addr add 10.0.1.10/24 dev eth1

ip netns exec analyzer_monitor ip -6 addr add fd00:1::10/64 dev eth1

ip netns exec analyzer_monitor ip link set eth1 up

ip netns exec analyzer_monitor ip link set lo up




# Запуск DHCP (IPv4 + IPv6) для Monitor

ip netns exec analyzer_monitor dnsmasq --interface=eth1 --bind-interfaces \

 --dhcp-range=10.0.1.20,10.0.1.20,255.255.255.0,12h \

 --dhcp-range=fd00:1::20,fd00:1::20,64,12h --enable-ra \

 --pid-file=/tmp/dnsmasq_monitor.pid




# ==========================================

# Настройка Sender (eth2)

# ==========================================

ip netns exec analyzer_sender ip addr add 10.0.2.10/24 dev eth2

ip netns exec analyzer_sender ip -6 addr add fd00:2::10/64 dev eth2

ip netns exec analyzer_sender ip link set eth2 up

ip netns exec analyzer_sender ip link set lo up




# Запуск DHCP (IPv4 + IPv6) для Sender

ip netns exec analyzer_sender dnsmasq --interface=eth2 --bind-interfaces \

 --dhcp-range=10.0.2.20,10.0.2.20,255.255.255.0,12h \

 --dhcp-range=fd00:2::20,fd00:2::20,64,12h --enable-ra \

 --pid-file=/tmp/dnsmasq_sender.pid




echo "Network setup complete. IPv4 and IPv6 isolated modes active."

muk0015@raspberrypi:~/diploma_project$

и еще я бы все таки хотел с тобой поговорить по поводу репозитория со всеми файлами, все-таки в моей рабочей папке диплома 29 элементов и может все таки имеет смысл это куда-нибудь выгрузить чтобы ты имел полное представление и понимание, так как видишь я тебе пересылал файлы по одному и ты так и не знал например о существовании файла coffee.bib
```

---

# Эксперимент 02.08.2026 — SLAAC против stateful DHCPv6

Стенд собран дома: Raspberry Pi (`eth1`/`eth2` через USB/LAN) двумя кабелями
соединена с ноутбуком Huawei (Arch Linux, NetworkManager), который выступает
целевым ПК вместо лабораторного. Пары портов установлены по MAC в поле
`Source link-layer address` полученных RA:

| Малина | netns | Префикс | Порт Huawei |
|---|---|---|---|
| `eth1` `00:e0:4c:68:02:64` | `analyzer_monitor` | `fd00:1::/64` | `enp0s20f0u4u1` `00:e0:4c:68:02:16` |
| `eth2` `00:e0:4c:68:02:23` | `analyzer_sender` | `fd00:2::/64` | `enp0s20f0u4u2` `00:e0:4c:68:02:01` |

## Исходное состояние цели

До запуска `setup_network.sh` оба порта Huawei: `UP,LOWER_UP`, только link-local
`fe80::`, маршрутные таблицы пусты, NetworkManager в состоянии `disconnected`
с профилем `--`, `accept_ra = 0` (NM отключает обработку RA в ядре, разбирая её
сам в userspace при активном профиле). `net.ipv6.conf.default.accept_ra = 1` —
заводское значение ядра, то есть ноль выставлен NM, а не является нормой.

`rdisc6` сначала не отправлял Router Solicitation: `Cannot assign requested
address`. Причина — отсутствие маршрута до групповых адресов на интерфейсе
(link-local адрес помечен `noprefixroute`). Обход для диагностики:
`ip -6 route add ff02::/16 dev <if>`. В штатной работе не нужен — маршрут
появляется сам при активном сетевом профиле.

## Замер 1: конфигурация как в репозитории (stateful DHCPv6)

`--dhcp-range=fd00:1::20,fd00:1::20,64,12h --enable-ra`

Вывод `rdisc6`, оба порта идентичны:

```
Stateful address conf. : Yes      <- M-флаг
Stateful other conf.   : Yes      <- O-флаг
Prefix                 : fd00:1::/64
On-link                : Yes
Autonomous address conf.: No      <- A-флаг снят
Router lifetime        : 1800 seconds
```

Блокирующих фактора два, а не один. M-флаг отправляет цель за адресом к
DHCPv6-серверу; A-флаг, снятый у самого префикса, дополнительно запрещает
строить из него адрес автоконфигурацией. dnsmasq выставляет оба именно так,
когда диапазон задан конкретным адресом.

## Замер 2: добавлено ключевое слово `slaac`

Перезапущен только monitor-netns, sender оставлен без изменений как контрольный
образец. Одно устройство, два режима одновременно.

`--dhcp-range=fd00:1::20,fd00:1::20,slaac,64,12h --enable-ra`

`Autonomous address conf.` перешёл в `Yes`, на sender-порту остался `No`.
После `sysctl -w net.ipv6.conf.<if>.accept_ra=1` на цели:

```
enp0s20f0u4u1 (monitor, A=1):
  fd00:1::2e0:4cff:fe68:216/64  dynamic mngtmpaddr proto kernel_ra
  fd00:1::20/128                dynamic noprefixroute
  fd00:1::1658:585c:165d:5cc5/64 dynamic noprefixroute
  fe80::fa98:9194:1921:e0d6/64

enp0s20f0u4u2 (sender, A=0):
  fd00:2::20/128                dynamic noprefixroute
  fe80::6a35:c335:817c:85ad/64
```

Ключевая строка — `fd00:1::2e0:4cff:fe68:216` с меткой **`proto kernel_ra`**:
адрес построен ядром из Router Advertisement без единого процесса в пространстве
пользователя. Интерфейсный идентификатор — MAC цели `00:e0:4c:68:02:16` по
EUI-64, то есть адрес соседа вычислим и не требует жёсткой прописи в коде.
На sender-порту при снятом A-флаге такого адреса нет.

Проверка проходимости из `analyzer_monitor`: `10.0.1.20` и
`fd00:1::2e0:4cff:fe68:216` отвечают, 0% потерь, RTT около 1 мс.

## Побочный результат: NetworkManager настраивает цель сам

После появления в сегменте отвечающего сервера NM создал профили `Wired
connection 1` и `Wired connection 2`, получил `10.0.1.20` и `10.0.2.20` по
DHCPv4, `fd00:1::20` и `fd00:2::20` по DHCPv6 и дополнительный SLAAC-адрес со
случайным идентификатором. Ручной `dhclient` на цели не понадобился нигде.

Отсюда уточнение формулировки для текста работы. Разница между протоколами не в
наличии ручного труда, а в необходимости процесса на цели: по IPv4 без
DHCP-клиента адреса не будет никогда, по IPv6 ядро выдаёт link-local сразу по
поднятию линка, а при поднятом A-флаге строит и глобальный адрес из префикса.

## Побочный результат: разгадан Nmap на 10.0.1.20

Одна команда, разные netns:

```
# ip netns exec analyzer_sender  nmap -F -T4 ... 10.0.1.20
setup_target: failed to determine route to 10.0.1.20
WARNING: No targets were specified, so 0 hosts scanned.

# ip netns exec analyzer_monitor nmap -F -T4 ... 10.0.1.20
Nmap scan report for 10.0.1.20
Host is up (0.00090s latency).
22/tcp closed ssh
MAC Address: 00:E0:4C:68:02:16 (Realtek Semiconductor)
```

Причина не в сети и не в цели, а в `gui_app.py`: режим LAN жёстко запускал
сканер в `analyzer_sender`, тогда как `10.0.1.20` находится за
`analyzer_monitor`, а namespace изолированы намеренно и маршрута между ними нет.
Исправлено методом `netns_for()` — выбор namespace по подсети цели.
