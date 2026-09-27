#!/bin/bash
# KP5: passive capture limit on the loop. UDP from snd0 to mon0 in steps, capture on mon0.
# Note: on the loop the same Pi also sends and receives the load.
D=/home/muk0015/diploma_project
MON=analyzer_monitor; SND=analyzer_sender
MON_LL=$(ip -n $MON -6 -br addr show mon0 | grep -o 'fe80::[^/]*')
LEN=${LEN:-1000}
OUT=/tmp/capture_limit.csv
ip netns exec $MON iperf3 -s -D
echo "streams;rate_mbit;len_B;iperf_sent;iperf_lost;captured_udp;tcpdump_dropped;capture_loss_pct;pps;cpu_python;cpu_tcpdump;cpu_total_busy;temp_start;temp_end;throttled" > $OUT
for RATE in ${RATES:-50 100 125 150 200 250}; do
    t0=$(vcgencmd measure_temp | grep -o '[0-9.]*')
    rm -f /tmp/cl.out /tmp/cl.json
    ip netns exec $MON python3 $D/sniff_stats.py mon0 --duration 26 > /tmp/cl.out 2>&1 &
    P=$!; sleep 3
    T=$(pgrep -P $P -x tcpdump)
    ip netns exec $SND iperf3 -c "$MON_LL%snd0" -u -b $((RATE / ${STREAMS:-1}))M -P ${STREAMS:-1} -t 20 -l $LEN -J > /tmp/cl.json &
    I=$!
    sleep 3
    pidstat -u -p $P,$T 1 14 > /tmp/cl_pid.txt &
    mpstat 1 14 > /tmp/cl_mp.txt &
    wait $I; wait $P
    wait
    t1=$(vcgencmd measure_temp | grep -o '[0-9.]*')
    th=$(vcgencmd get_throttled | cut -d= -f2)
    cp=$(awk '/^Average/ && $NF=="python3"{print $8}' /tmp/cl_pid.txt)
    ct=$(awk '/^Average/ && $NF=="tcpdump"{print $8}' /tmp/cl_pid.txt)
    busy=$(awk '/^Average/ && $2=="all"{printf "%.1f", 100-$NF}' /tmp/cl_mp.txt)
    python3 - "$RATE" "$LEN" "$cp" "$ct" "$busy" "$t0" "$t1" "$th" >> $OUT <<'EOF'
import json, sys
rate, length, cp, ct, busy, t0, t1, th = sys.argv[1:]
s = json.load(open("/tmp/cl.json"))["end"]["sum"]
r = json.loads(open("/tmp/cl.out").read().split("RESULT sniff_stats ", 1)[1])
udp = r["cats"]["UDP"][0]
received = s["packets"] - s["lost_packets"] + 2
loss = 100.0 * (received - udp) / received
print("%s;%s;%s;%d;%d;%d;%s;%.2f;%d;%s;%s;%s;%s;%s;%s" % (__import__("os").environ.get("STREAMS", "1"), rate, length, s["packets"], s["lost_packets"], udp,
      r["tcpdump"]["dropped"], loss, round(s["packets"] / s["seconds"]), cp, ct, busy, t0, t1, th))
EOF
    tail -1 $OUT
    sleep ${COOL:-5}
done
ip netns pids $MON | xargs -r ps -o pid=,comm= -p | awk '$2=="iperf3"{print $1}' | xargs -r kill
