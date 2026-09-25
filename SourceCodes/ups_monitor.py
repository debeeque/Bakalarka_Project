import argparse
import os
import signal
import subprocess
import sys
import time
from datetime import datetime

from smbus import SMBus

REG_SHUNT = 0x01
REG_BUS = 0x02
SHUNT_OHM = 0.010

# Preliminary linear model until a measured discharge curve replaces it
V_EMPTY = 9.6
V_FULL = 12.6


def swap(word):
    return ((word & 0xFF) << 8) | (word >> 8)


def read_once(bus, addr):
    raw = swap(bus.read_word_data(addr, REG_SHUNT))
    if raw & 0x8000:
        raw -= 0x10000
    v_bus = (swap(bus.read_word_data(addr, REG_BUS)) >> 3) * 0.004
    return v_bus, raw * 10e-6 / SHUNT_OHM


def sample(bus, addr, n):
    vs, cs = [], []
    for _ in range(n):
        try:
            v, i = read_once(bus, addr)
        except OSError:
            continue
        vs.append(v)
        cs.append(i)
        time.sleep(0.02)
    if not vs:
        return None
    return sum(vs) / len(vs), sum(cs) / len(cs)


def percent(v):
    return max(0.0, min(100.0, (v - V_EMPTY) / (V_FULL - V_EMPTY) * 100))


def one_shot(bus, args):
    s = sample(bus, args.addr, args.samples)
    if s is None:
        print("BATTERY ERROR")
        return 1
    v, i = s
    p, pct = v * i, percent(v)
    print(f"Bus voltage: {v:.3f} V")
    print(f"Current:     {i:+.3f} A")
    print(f"Power:       {p:+.2f} W")
    print(f"Charge:      {pct:.0f} % (preliminary, linear {V_EMPTY}-{V_FULL} V)")
    print(f"BATTERY V={v:.2f} I={i:.2f} P={p:.1f} PCT={pct:.0f}")
    return 0


def write(f, line):
    f.write(line + "\n")
    f.flush()
    os.fsync(f.fileno())


def log_loop(bus, args):
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    new = not os.path.exists(args.log) or os.path.getsize(args.log) == 0
    with open(args.log, "a") as f:
        if new:
            write(f, "t_mono_s,v_bus,i,p")
        write(f, f"# start {datetime.now().isoformat(timespec='seconds')} "
                 f"mono={time.monotonic():.1f} interval={args.interval} "
                 f"threshold={args.threshold} count={args.count}")
        low = 0
        next_t = time.monotonic()
        try:
            while True:
                s = sample(bus, args.addr, args.samples)
                t = time.monotonic()
                if s is None:
                    write(f, f"# {t:.1f} read error")
                else:
                    v, i = s
                    write(f, f"{t:.1f},{v:.3f},{i:.3f},{v * i:.2f}")
                    low = low + 1 if v < args.threshold else 0
                    if low >= args.count:
                        write(f, f"# {t:.1f} shutdown: v_bus < {args.threshold} V "
                                 f"in {low} consecutive readings")
                        if args.dry_run:
                            low = 0
                        else:
                            subprocess.run(["sudo", "shutdown", "-h", "now"])
                            return 0
                next_t += args.interval
                time.sleep(max(0.0, next_t - time.monotonic()))
        finally:
            write(f, f"# stop {time.monotonic():.1f}")


def main():
    parser = argparse.ArgumentParser(description="UPS Module 3S telemetry via INA219")
    parser.add_argument("--bus", type=int, default=3)
    parser.add_argument("--addr", type=lambda x: int(x, 0), default=0x41)
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--log")
    parser.add_argument("--interval", type=float, default=10)
    parser.add_argument("--threshold", type=float, default=V_EMPTY)
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    bus = SMBus(args.bus)
    if args.log:
        return log_loop(bus, args)
    return one_shot(bus, args)


if __name__ == "__main__":
    sys.exit(main())
