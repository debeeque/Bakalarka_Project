#!/usr/bin/env python3
# KP2 of the TRAFFIC screen: under an iperf3 TCP flow the GUI stays responsive for 10 minutes.
# A second GUI instance captures on mon0; every 100 ms a timer measures how late the Tk loop runs it,
# every 15 s the PAUSED page is opened and closed and the switch is timed.
import subprocess
import sys
import time
import tkinter as tk

sys.path.insert(0, "/home/muk0015/diploma_project")
import gui_app

DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 600
OUT = "/tmp/kp2_result.txt"
lags, switches, t0 = [], [], time.monotonic()


def main():
    root = tk.Tk()
    app = gui_app.AnalyzerApp(root)
    app.unlock()
    app.open("TRAFFIC")
    t = app.screens["TRAFFIC"]
    t.select_port("mon0")
    t.start()
    target = subprocess.run(["sudo", "ip", "-n", "analyzer_monitor", "-6", "-o", "addr", "show", "mon0"],
                            capture_output=True, text=True).stdout
    t6 = [w.split("/")[0] for w in target.split() if w.startswith("fd00:2::")][0]
    load = subprocess.Popen(["sudo", "ip", "netns", "exec", "analyzer_sender", "iperf3", "-c", t6, "-t",
                             str(int(DURATION)), "-i", "0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def probe(expected):
        now = time.monotonic()
        lags.append((now - expected) * 1000)
        if now - t0 < DURATION:
            root.after(100, probe, now + 0.1)
        else:
            finish()

    def switch():
        a = time.monotonic()
        app.open("PAUSED")
        root.update_idletasks()
        b = time.monotonic()
        app.open("TRAFFIC")
        root.update_idletasks()
        switches.append(((b - a) * 1000, (time.monotonic() - b) * 1000))
        if time.monotonic() - t0 < DURATION:
            root.after(15000, switch)

    def finish():
        load.terminate()
        t.stop()
        root.after(4000, report)

    def report():
        s = sorted(lags)
        p99 = s[int(len(s) * 0.99)] if s else 0
        res = (t.last or {}).get("result") or {}
        with open(OUT, "w") as f:
            f.write("duration_s %.0f probes %d lag_max_ms %.0f lag_p99_ms %.0f lag_over_300 %d\n" % (
                time.monotonic() - t0, len(lags), max(s or [0]), p99, sum(1 for x in s if x > 300)))
            f.write("switch_to_paused_ms max %.0f  back_to_traffic_ms max %.0f  n %d\n" % (
                max(a for a, _ in switches), max(b for _, b in switches), len(switches)))
            f.write("capture packets %s  dropped_by_kernel %s  stopped %s\n" % (
                res.get("packets"), (res.get("tcpdump") or {}).get("dropped"), res.get("stopped")))
        root.destroy()

    root.after(100, probe, time.monotonic() + 0.1)
    root.after(15000, switch)
    root.mainloop()


if __name__ == "__main__":
    main()
