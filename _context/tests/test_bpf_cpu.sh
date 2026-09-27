#!/bin/bash
# KP6: CPU of the capture with and without a kernel BPF filter, TCP load in the background
D=/home/muk0015/diploma_project
MON=analyzer_monitor; SND=analyzer_sender
MON_LL=$(ip -n $MON -6 -br addr show mon0 | grep -o 'fe80::[^/]*')
ip netns exec $MON iperf3 -s -D
run() {
    rm -f /tmp/k6.out
    ip netns exec $MON python3 $D/sniff_stats.py mon0 $1 --duration 22 > /tmp/k6.out 2>&1 &
    P=$!; sleep 3
    T=$(pgrep -P $P -x tcpdump)
    ip netns exec $SND iperf3 -c "$MON_LL%snd0" -t 18 -b 50M > /tmp/k6_iperf.txt &
    ip netns exec $SND ping -6 -c 60 -i 0.25 -q "$MON_LL%snd0" > /dev/null &
    sleep 2
    pidstat -u -p $P,$T 1 12 | grep -E "^Average" | awk '{printf "    %-8s %%usr %s %%system %s %%CPU %s\n", $NF, $4, $5, $8}'
    wait $P
    grep '^RESULT' /tmp/k6.out | cut -d' ' -f3- | python3 -c "
import json,sys; r=json.load(sys.stdin)
print('    packets', r['packets'], {k: v[0] for k, v in r['cats'].items() if v[0]}, 'dropped', r['tcpdump']['dropped'])"
    grep receiver /tmp/k6_iperf.txt | awk '{print "    iperf3", $7, $8}'
    wait
}
echo "=== no filter"; run ""
echo "=== --bpf icmp6"; run "--bpf icmp6"
ip netns pids $MON | xargs -r ps -o pid=,comm= -p | awk '$2=="iperf3"{print $1}' | xargs -r kill
