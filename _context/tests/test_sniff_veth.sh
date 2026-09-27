#!/bin/bash
# veth test bench for sniff_stats.py: two temporary namespaces, mixed traffic,
# result compared with tcpdump -r and capinfos on the same pcap
D=/home/muk0015/diploma_project
A=st_a; B=st_b
cleanup() { ip netns pids $A 2>/dev/null | xargs -r kill; ip netns pids $B 2>/dev/null | xargs -r kill; ip netns del $A 2>/dev/null; ip netns del $B 2>/dev/null; }
cleanup
ip netns add $A; ip netns add $B
ip link add va netns $A type veth peer name vb netns $B
ip -n $A addr add 10.99.0.1/24 dev va; ip -n $B addr add 10.99.0.2/24 dev vb
ip -n $A -6 addr add fd99::1/64 dev va nodad; ip -n $B -6 addr add fd99::2/64 dev vb nodad
for n in $A $B; do ip -n $n link set lo up; done
ip -n $A link set va up; ip -n $B link set vb up
sleep 2
rm -f /tmp/st.pcap /tmp/st.csv /tmp/st_top.csv /tmp/st.out /tmp/iperf_udp.json
ip netns exec $B iperf3 -s -D
ip netns exec $B python3 $D/sniff_stats.py vb --pcap /tmp/st.pcap --csv /tmp/st.csv --duration 20 > /tmp/st.out 2>&1 &
S=$!
sleep 2
ip netns exec $A ping -c 50 -i 0.05 -q 10.99.0.2 >/dev/null
ip netns exec $A ping -6 -c 50 -i 0.05 -q fd99::2 >/dev/null
ip netns exec $A iperf3 -c 10.99.0.2 -t 3 -b 20M >/dev/null
ip netns exec $A iperf3 -c fd99::2 -u -t 3 -b 5M -l 1000 -J > /tmp/iperf_udp.json
wait $S
cleanup
echo "--- script output (without STATS lines):"
grep -v "^STATS" /tmp/st.out | cut -c1-400
echo "--- STATS lines: $(grep -c '^STATS' /tmp/st.out)"
echo "--- reference from the same pcap:"
for f in tcp udp icmp icmp6 arp; do printf "  %-6s %s\n" $f "$(tcpdump -r /tmp/st.pcap -n $f 2>/dev/null | wc -l)"; done
capinfos -c /tmp/st.pcap | tail -1
python3 -c "import json;d=json.load(open('/tmp/iperf_udp.json'));print('  iperf3 UDP sender packets:', d['end']['sum']['packets'] if 'packets' in d['end']['sum'] else d['end']['sum'])"
echo "--- csv:"; head -4 /tmp/st.csv; echo ...; cat /tmp/st_top.csv
