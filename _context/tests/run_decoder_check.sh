#!/bin/bash
D=/home/muk0015/diploma_project
rm -f /tmp/dec.pcap
ip netns exec analyzer_monitor python3 $D/sniff_stats.py mon0 --pcap /tmp/dec.pcap --duration 22 > /tmp/dec.out 2>&1 &
S=$!; sleep 3
$D/setup_network.sh dhcp
sleep 2
ip netns exec analyzer_sender python3 /tmp/gen_test_frames.py snd0
cd $D && ip netns exec analyzer_sender python3 ra_audit.py snd0 -t 3 > /tmp/ra_audit.out 2>&1
wait $S
$D/setup_network.sh nodhcp
grep '^RESULT' /tmp/dec.out | cut -c1-200
python3 /tmp/validate_decoder.py /tmp/dec.pcap
echo "--- ra_audit on snd0:"; grep -E "^--- Router|Source  |Flags|Prefix|MTU|Router life" /tmp/ra_audit.out
