import re
import struct
import subprocess
import sys

sys.path.insert(0, "/home/muk0015/diploma_project")
from pktdecode import DHCP4_TYPES, DHCP6_TYPES, PREFERENCE, describe

MULTI = ["icmpv6.opt.prefix", "icmpv6.opt.prefix.length", "icmpv6.opt.prefix.flag.l", "icmpv6.opt.prefix.flag.a",
         "icmpv6.opt.prefix.valid_lifetime", "icmpv6.opt.prefix.preferred_lifetime", "icmpv6.opt.mtu",
         "icmpv6.opt.linkaddr", "icmpv6.opt.rdnss"]
SINGLE = ["eth.src", "eth.dst", "eth.type", "vlan.id", "ip.src", "ip.dst", "ip.ttl", "ip.len", "ip.id", "ip.proto",
          "ip.frag_offset", "ipv6.src", "ipv6.dst", "ipv6.hlim", "ipv6.plen", "ipv6.nxt", "tcp.srcport",
          "tcp.dstport", "tcp.flags", "tcp.seq_raw", "tcp.ack_raw", "tcp.window_size_value", "udp.srcport",
          "udp.dstport", "udp.length", "icmp.type", "icmp.code", "icmp.ident", "icmp.seq", "icmpv6.type",
          "icmpv6.code", "icmpv6.echo.identifier", "icmpv6.echo.sequence_number", "icmpv6.mtu",
          "icmpv6.nd.ra.cur_hop_limit", "icmpv6.nd.ra.flag.m", "icmpv6.nd.ra.flag.o", "icmpv6.nd.ra.flag.prf",
          "icmpv6.nd.ra.router_lifetime", "icmpv6.nd.ra.reachable_time", "icmpv6.nd.ra.retrans_timer",
          "icmpv6.nd.ns.target_address", "icmpv6.nd.na.target_address", "icmpv6.nd.na.flag.r",
          "icmpv6.nd.na.flag.s", "icmpv6.nd.na.flag.o", "arp.opcode", "arp.src.proto_ipv4", "arp.dst.proto_ipv4",
          "arp.src.hw_mac", "dhcp.option.dhcp", "dhcp.hw.mac_addr", "dhcp.ip.your", "dhcpv6.msgtype",
          "dns.qry.name", "dns.qry.type", "dns.flags.response", "dns.id"]
TCPF = "FSRPAUEC"
PRF = {v: k for k, v in PREFERENCE.items()}
D4 = {v: k for k, v in DHCP4_TYPES.items()}
D6 = {v: k for k, v in DHCP6_TYPES.items()}


def frames(path):
    with open(path, "rb") as f:
        head = f.read(24)
        order = "<" if struct.unpack("<I", head[:4])[0] in (0xA1B2C3D4, 0xA1B23C4D) else ">"
        while True:
            h = f.read(16)
            if len(h) < 16:
                return
            incl = struct.unpack(order + "IIII", h)[2]
            yield f.read(incl)


def norm(v):
    v = v.strip().lower()
    if v in ("true", "false"):
        return "1" if v == "true" else "0"
    try:
        return str(int(v, 0))
    except ValueError:
        return v


def life(v):
    v = v.split()[0]
    return "4294967295" if v == "infinite" else v


def ours(data):
    out = {}

    def put(k, v):
        out.setdefault(k, []).append(norm(str(v)))

    layer, icmp6_type = "", None
    for lay, text in describe(data):
        if lay:
            layer = lay
        m = None
        if lay == "Ethernet":
            m = re.match(r"(\S+) > (\S+)\s+type 0x([0-9a-f]{4})", text)
            put("eth.src", m[1]); put("eth.dst", m[2]); put("eth.type", int(m[3], 16))
        elif lay == "802.1Q":
            put("vlan.id", re.search(r"VLAN (\d+)", text)[1])
        elif layer == "IPv4":
            m = re.match(r"(\S+) > (\S+)$", text)
            if m:
                put("ip.src", m[1]); put("ip.dst", m[2])
            m = re.search(r"ttl (\d+)\s+length (\d+)\s+id 0x([0-9a-f]+)\s+\S+\s+proto (\d+)", text)
            if m:
                put("ip.ttl", m[1]); put("ip.len", m[2]); put("ip.id", int(m[3], 16)); put("ip.proto", m[4])
            m = re.search(r"fragment offset (\d+) B", text)
            if m:
                put("ip.frag_offset", int(m[1]) // 8)
        elif layer == "IPv6":
            m = re.match(r"(\S+) > (\S+)$", text)
            if m:
                put("ipv6.src", m[1]); put("ipv6.dst", m[2])
            m = re.search(r"hop limit (\d+)\s+payload (\d+) B\s+next header (\d+)", text)
            if m:
                put("ipv6.hlim", m[1]); put("ipv6.plen", m[2])
                if "   ext " not in text:
                    put("ipv6.nxt", m[3])
        elif lay == "TCP":
            m = re.match(r"(\d+) > (\d+)\s+flags \[(\w*)\]\s+seq (\d+)\s+ack (\d+)\s+win (\d+)", text)
            put("tcp.srcport", m[1]); put("tcp.dstport", m[2])
            put("tcp.flags", sum(1 << TCPF.index(c) for c in m[3]))
            put("tcp.seq_raw", m[4]); put("tcp.ack_raw", m[5]); put("tcp.window_size_value", m[6])
        elif lay == "UDP":
            m = re.match(r"(\d+) > (\d+)\s+length (\d+)", text)
            put("udp.srcport", m[1]); put("udp.dstport", m[2]); put("udp.length", m[3])
        elif lay == "ICMP":
            m = re.match(r"type (\d+).*?code (\d+)(?:\s+id (\d+)\s+seq (\d+))?", text)
            put("icmp.type", m[1]); put("icmp.code", m[2])
            if m[3]:
                put("icmp.ident", m[3]); put("icmp.seq", m[4])
        elif lay == "ICMPv6":
            m = re.match(r"type (\d+).*?code (\d+)", text)
            icmp6_type = int(m[1])
            put("icmpv6.type", m[1]); put("icmpv6.code", m[2])
            m = re.search(r"id (\d+)\s+seq (\d+)", text)
            if m:
                put("icmpv6.echo.identifier", m[1]); put("icmpv6.echo.sequence_number", m[2])
            m = re.search(r"MTU (\d+)", text)
            if m:
                put("icmpv6.mtu", m[1])
        elif layer == "ICMPv6" and not lay:
            m = re.match(r"M=(\d) O=(\d)\s+preference (\w+)\s+cur hop limit (\d+)", text)
            if m:
                put("icmpv6.nd.ra.flag.m", m[1]); put("icmpv6.nd.ra.flag.o", m[2])
                put("icmpv6.nd.ra.flag.prf", PRF[m[3]]); put("icmpv6.nd.ra.cur_hop_limit", m[4])
            m = re.match(r"router lifetime (\d+) s\s+reachable (\d+) ms\s+retrans (\d+) ms", text)
            if m:
                put("icmpv6.nd.ra.router_lifetime", m[1]); put("icmpv6.nd.ra.reachable_time", m[2])
                put("icmpv6.nd.ra.retrans_timer", m[3])
            m = re.match(r"target (\S+)(?:\s+R=(\d) S=(\d) O=(\d))?", text)
            if m:
                if icmp6_type == 135:
                    put("icmpv6.nd.ns.target_address", m[1])
                else:
                    put("icmpv6.nd.na.target_address", m[1])
                    put("icmpv6.nd.na.flag.r", m[2]); put("icmpv6.nd.na.flag.s", m[3]); put("icmpv6.nd.na.flag.o", m[4])
        elif lay == "option":
            m = re.match(r"prefix (\S+)/(\d+)\s+L=(\d) A=(\d)\s+valid (\S+ ?s?)\s+pref (\S+)", text)
            if m:
                put("icmpv6.opt.prefix", m[1]); put("icmpv6.opt.prefix.length", m[2])
                put("icmpv6.opt.prefix.flag.l", m[3]); put("icmpv6.opt.prefix.flag.a", m[4])
                put("icmpv6.opt.prefix.valid_lifetime", life(m[5])); put("icmpv6.opt.prefix.preferred_lifetime", life(m[6]))
            m = re.match(r"MTU (\d+)", text)
            if m:
                put("icmpv6.opt.mtu", m[1])
            m = re.match(r"(?:source|target) link-layer (\S+)", text)
            if m:
                put("icmpv6.opt.linkaddr", m[1])
            m = re.match(r"RDNSS (.+?)\s+lifetime", text)
            if m:
                for a in m[1].split(", "):
                    put("icmpv6.opt.rdnss", a)
        elif lay == "ARP":
            m = re.match(r"who-has (\S+) tell (\S+)", text)
            if m:
                put("arp.opcode", 1); put("arp.dst.proto_ipv4", m[1]); put("arp.src.proto_ipv4", m[2])
            m = re.match(r"(\S+) is-at (\S+)", text)
            if m:
                put("arp.opcode", 2); put("arp.src.proto_ipv4", m[1]); put("arp.src.hw_mac", m[2])
        elif lay == "DHCP":
            m = re.match(r"(\S+) (?:request|reply)\s+client (\S+)\s+your address (\S+)", text)
            put("dhcp.option.dhcp", D4[m[1]]); put("dhcp.hw.mac_addr", m[2]); put("dhcp.ip.your", m[3])
        elif lay == "DHCPv6":
            put("dhcpv6.msgtype", D6[text.split()[0]])
        elif lay == "DNS":
            m = re.match(r"(query|response)\s+(\S+)\s+type (\d+)\s+id 0x([0-9a-f]+)", text)
            put("dns.flags.response", 1 if m[1] == "response" else 0); put("dns.qry.name", m[2])
            put("dns.qry.type", m[3]); put("dns.id", int(m[4], 16))
    return out


def tshark(path, fields, occ):
    cmd = ["tshark", "-r", path, "-o", "ip.defragment:FALSE", "-o", "ipv6.defragment:FALSE", "-T", "fields", "-E", "occurrence=" + occ, "-E", "aggregator=|"]
    for f in fields:
        cmd += ["-e", f]
    rows = []
    for line in subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines():
        cols = line.split("\t")
        rows.append({f: [norm(x) for x in c.split("|")] for f, c in zip(fields, cols) if c})
    return rows


def main():
    path = sys.argv[1]
    single = tshark(path, SINGLE, "f")
    multi = tshark(path, MULTI, "a")
    total = bad = 0
    for i, data in enumerate(frames(path)):
        mine = ours(data)
        ref = dict(single[i])
        ref.update(multi[i])
        errs = []
        for field, values in mine.items():
            total += 1
            want = ref.get(field)
            if field in MULTI:
                ok = want is not None and sorted(values) == sorted(want)
            else:
                ok = want is not None and values[0] == want[0]
            if not ok:
                errs.append("%s ours=%s tshark=%s" % (field, values, want))
        missing = sorted(f for f in ref if f not in mine)
        bad += len(errs)
        head = describe(data)
        kind = next((t for lay, t in head if lay in ("ICMP", "ICMPv6", "ARP", "DHCP", "DHCPv6", "DNS", "TCP", "UDP")), head[0][1])
        print("%3d %-58s fields %2d  %s" % (i + 1, kind[:58], len(mine), "OK" if not errs else "MISMATCH"))
        for e in errs:
            print("      " + e)
        if missing:
            print("      not decoded (tshark has): " + ", ".join(sorted(missing)))
    print("frames %d, fields compared %d, mismatches %d" % (len(single), total, bad))


if __name__ == "__main__":
    main()
