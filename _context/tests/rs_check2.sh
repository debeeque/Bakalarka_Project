#!/bin/bash
rm -f /tmp/rs_check.pcap
ip netns exec analyzer_sender tcpdump -i snd0 -n -e -U -w /tmp/rs_check.pcap 'icmp6 or arp or (ip and not tcp)' 2>/dev/null &
TD=$!
sleep 2
ip -n analyzer_monitor link set mon0 down
sleep 2
/home/muk0015/diploma_project/setup_network.sh port mon0
sleep 25
kill $TD; sleep 1
tcpdump -r /tmp/rs_check.pcap -n -e -tttt 2>/dev/null | cut -c12-200
echo "RS count: $(tcpdump -r /tmp/rs_check.pcap -n 2>/dev/null | grep -c 'router solicitation')"
