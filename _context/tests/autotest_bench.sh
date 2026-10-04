#!/bin/sh
# Bench for autotest.py on the loop snd0 <-> mon0: a small "network" on snd0 with DHCP (router and DNS),
# RA with SLAAC and a default router, and a local name stand.test. Not device code.
#   sudo sh autotest_bench.sh start   |   sudo sh autotest_bench.sh stop
# A second server for the WARN case: fake_dhcp.py
NS=analyzer_sender
case "$1" in
start)
    ip netns exec $NS dnsmasq --interface=snd0 --bind-interfaces --no-resolv --no-hosts \
        --dhcp-range=10.0.2.50,10.0.2.60,255.255.255.0,1h \
        --dhcp-option=option:router,10.0.2.10 --dhcp-option=option:dns-server,10.0.2.10 \
        --dhcp-range=fd00:2::,ra-only,64 --enable-ra \
        --host-record=stand.test,10.0.2.10,fd00:2::10 \
        --dhcp-leasefile=/tmp/bench_dnsmasq.leases --pid-file=/tmp/bench_dnsmasq.pid
    ;;
stop)
    [ -f /tmp/bench_dnsmasq.pid ] && kill $(cat /tmp/bench_dnsmasq.pid) && rm -f /tmp/bench_dnsmasq.pid
    ;;
esac
