#!/bin/bash
# pkt_gen.py on the physical loop: send from snd0, count on mon0
D=/home/muk0015/diploma_project
MON=analyzer_monitor; SND=analyzer_sender
MON_LL=$(ip -n $MON -6 -br addr show mon0 | grep -o 'fe80::[^/]*')
count() {
    ip netns exec $MON python3 $D/sniff_stats.py mon0 --bpf "$1" --pcap /tmp/pgl.pcap > /tmp/pgl.out 2>&1 &
    S=$!; sleep 2
    shift
    ip netns exec $SND python3 $D/pkt_gen.py snd0 "$@" | grep -E "^(Sending|Sent|Error|Note|RESULT)" | cut -c1-330
    sleep 1; kill -TERM $S; wait $S
    grep '^RESULT' /tmp/pgl.out | cut -d' ' -f3- | python3 -c "
import json,sys; r=json.load(sys.stdin)
print('  MONITOR counted', r['packets'], 'avg', r['avg'], {k: v[0] for k, v in r['cats'].items() if v[0]}, 'dropped', r['tcpdump']['dropped'])"
}
rx() { ip -n $MON -s -j link show mon0 | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['stats64']['rx']['packets'])"; }

echo "=== KP1: 1000 ICMPv6 echo request at 100 pkt/s, snd0 -> mon0, counted with ND/RA around"
count "icmp6 and ip6[40] == 128" --proto icmp6 --dst $MON_LL --count 1000 --rate 100
echo "=== KP2: --size 200 (ICMPv6) and --size 1000 (UDP v6)"
count "icmp6 and ip6[40] == 128" --proto icmp6 --dst $MON_LL --count 500 --rate 500 --size 200
count "udp" --proto udp --dst $MON_LL --count 500 --rate 500 --size 1000
echo "=== KP3: maximum rate, received counted by the mon0 NIC counter"
for spec in "100 20000" "100 0" "1514 0"; do
    set -- $spec
    before=$(rx)
    ip netns exec $SND python3 $D/pkt_gen.py snd0 --proto udp --dst $MON_LL --count 100000 --rate $2 --size $1 | grep '^RESULT' | cut -d' ' -f3- > /tmp/pgmax.json
    sleep 1
    after=$(rx)
    python3 - $1 $2 $before $after <<'EOF'
import json, sys
size, rate, before, after = sys.argv[1:]
r = json.load(open("/tmp/pgmax.json"))
got = int(after) - int(before)
print("  size %s B, rate %s: sent %d at %d pkt/s (%.1f Mbit/s), cpu %s %%, mon0 received %d, loss %.2f %%, send errors %d"
      % (size, rate if rate != "0" else "max", r["sent"], r["rate_real"], r["rate_real"] * r["frame_len"] * 8 / 1e6,
         r["cpu_pct"], got, 100.0 * (r["sent"] - got) / r["sent"], r["errors"]))
EOF
done
echo "=== KP4: RS from snd0 with DHCP/RA on, the answer seen on mon0"
$D/setup_network.sh dhcp > /dev/null
sleep 1
count "icmp6 and (ip6[40] == 133 or ip6[40] == 134)" --proto rs --count 1
$D/setup_network.sh nodhcp > /dev/null
python3 - <<'EOF'
import struct, sys
sys.path.insert(0, "/home/muk0015/diploma_project")
from pktdecode import describe
f = open("/tmp/pgl.pcap", "rb"); f.read(24)
while True:
    h = f.read(16)
    if len(h) < 16: break
    data = f.read(struct.unpack("<IIII", h)[2])
    lines = describe(data)
    kind = [t for l, t in lines if l == "ICMPv6"][0]
    print("  frame:", kind.split("   ")[0], "from", [t for l, t in lines if l == "Ethernet"][0].split()[0])
    if "134" in kind:
        for l, t in lines:
            print("     %-8s %s" % (l, t))
EOF
