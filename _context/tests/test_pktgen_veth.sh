#!/bin/bash
# pkt_gen.py on a veth pair: sender in pg_a, counting with sniff_stats.py in pg_b
D=/home/muk0015/diploma_project
A=pg_a; B=pg_b
cleanup() { for n in $A $B; do ip netns pids $n 2>/dev/null | xargs -r kill; ip netns del $n 2>/dev/null; done; }
cleanup
ip netns add $A; ip netns add $B
ip link add va netns $A type veth peer name vb netns $B
ip -n $A addr add 10.0.2.10/24 dev va; ip -n $B addr add 10.0.2.20/24 dev vb
for n in $A $B; do ip -n $n link set lo up; done
ip -n $A link set va up; ip -n $B link set vb up
sleep 3
LL_B=$(ip -n $B -6 -br addr show vb | grep -o 'fe80::[^/]*')
count() {
    ip netns exec $B python3 $D/sniff_stats.py vb --bpf "$1" > /tmp/pg.out 2>&1 &
    S=$!; sleep 2
    shift 2
    ip netns exec $A python3 $D/pkt_gen.py va "$@" | grep -E "^(Sending|Sent|Error|Note)"
    sleep 1
    t=$(date +%s.%N); kill -TERM $S; wait $S
    echo "  STOP took $(echo "$(date +%s.%N) - $t" | bc | cut -c1-5) s"
    grep '^RESULT' /tmp/pg.out | cut -d' ' -f3- | python3 -c "
import json,sys; r=json.load(sys.stdin)
print('  received', r['packets'], 'avg', r['avg'], {k: v[0] for k, v in r['cats'].items() if v[0]})"
}
echo "=== 1000 ICMPv6 echo at 100 pkt/s to $LL_B (NS resolves the MAC)"
count "icmp6 and ip6[40] == 128" 15 --proto icmp6 --dst $LL_B --count 1000 --rate 100
echo "=== 300 UDP v4 --size 512"
count "udp" 8 --proto udp --dst 10.0.2.20 --count 300 --rate 200 --size 512
echo "=== 3 RS"
count "icmp6 and ip6[40] == 133" 6 --proto rs --count 3 --rate 1
echo "=== outside the bench must be refused"
ip netns exec $A python3 $D/pkt_gen.py va --proto udp --dst 8.8.8.8 --count 1 | cut -c1-160; echo "exit $?"
cleanup
