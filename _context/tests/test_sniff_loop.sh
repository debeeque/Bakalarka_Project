#!/bin/bash
# sniff_stats.py on the physical loop mon0 <-> snd0
D=/home/muk0015/diploma_project
MON=analyzer_monitor; SND=analyzer_sender
MON_LL=$(ip -n $MON -6 -br addr show mon0 | grep -o 'fe80::[^/]*')
off() { ip netns exec $MON ethtool -k mon0 | grep -E "^(generic-receive|generic-segmentation|tcp-segmentation)-offload" | tr '\n' ' '; echo; }
stop_iperf() { ip netns pids $MON | xargs -r ps -o pid=,comm= -p | awk '$2=="iperf3"{print $1}' | xargs -r kill; }
summary() {
    grep -v '^STATS' $1 | grep -v '^RESULT'
    grep '^RESULT' $1 | cut -d' ' -f3- | python3 -c "
import json,sys; r=json.load(sys.stdin)
print('  RESULT packets', r['packets'], 'cats', {k: v[0] for k, v in r['cats'].items()}, 'tcpdump', r['tcpdump'], 'offload', r['offload'])"
}

echo "offload before: $(off)"
ip netns exec $MON iperf3 -s -D

exit_kp1=1; echo "=== KP2: 100 ping v4, 100 ping v6, iperf3 TCP 5 s"
ip -n $SND addr add 10.0.1.20/24 dev snd0
rm -f /tmp/k2.pcap /tmp/k2.out
ip netns exec $MON python3 $D/sniff_stats.py mon0 --pcap /tmp/k2.pcap --max-mb 200 --csv /tmp/k2.csv --duration 26 > /tmp/k2.out 2>&1 &
S=$!; sleep 3
ip netns exec $SND ping -c 100 -i 0.05 -q -I 10.0.1.20 10.0.1.10 | tail -1
ip netns exec $SND ping -6 -c 100 -i 0.05 -q "$MON_LL%snd0" | tail -1
ip netns exec $SND iperf3 -c "$MON_LL%snd0" -t 5 -b 20M | grep -E "receiver"
wait $S
ip -n $SND addr del 10.0.1.20/24 dev snd0
summary /tmp/k2.out
for f in tcp udp icmp icmp6 arp; do printf "  tcpdump -r %-6s %s\n" $f "$(tcpdump -r /tmp/k2.pcap -n $f 2>/dev/null | wc -l)"; done
echo "  tshark icmpv6: $(tshark -r /tmp/k2.pcap -Y icmpv6 2>/dev/null | wc -l)"
echo "  capinfos: $(capinfos -c /tmp/k2.pcap | tail -1)"
echo "  max frame length: $(tshark -r /tmp/k2.pcap -T fields -e frame.len 2>/dev/null | sort -n | tail -1)"
echo "offload after: $(off)"
stop_iperf
