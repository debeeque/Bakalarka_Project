#!/bin/bash
# Usage: setup_network.sh [ports|dhcp|nodhcp]
#   ports   namespaces, addresses and links only; nothing is served
#   dhcp    start DHCP and RA on both ports (sets the ports up if missing)
#   nodhcp  stop DHCP and RA
#   no argument: ports and dhcp

# Deleting a namespace returns its physical interfaces asynchronously
wait_for_iface() {
    for _ in $(seq 1 50); do
        [ -e "/sys/class/net/$1" ] && return 0
        sleep 0.1
    done
    echo "Error: interface $1 did not return to the default namespace"
    return 1
}

setup_ports() {
    killall dnsmasq 2>/dev/null

    # A process left inside a namespace keeps it alive after deletion
    # and the physical interface never returns
    for ns in analyzer_monitor analyzer_sender; do
        pids=$(ip netns pids $ns 2>/dev/null)
        [ -n "$pids" ] && kill $pids 2>/dev/null
    done
    ip netns delete analyzer_monitor 2>/dev/null
    ip netns delete analyzer_sender 2>/dev/null

    wait_for_iface eth1 || exit 1
    wait_for_iface eth2 || exit 1

    # Create new isolated network namespaces
    ip netns add analyzer_monitor
    ip netns add analyzer_sender

    # Assign physical interfaces to namespaces
    ip link set dev eth1 netns analyzer_monitor
    ip link set dev eth2 netns analyzer_sender

    # Monitor interface (eth1)
    ip netns exec analyzer_monitor ip addr add 10.0.1.10/24 dev eth1
    ip netns exec analyzer_monitor ip -6 addr add fd00:1::10/64 dev eth1
    ip netns exec analyzer_monitor ip link set eth1 up
    ip netns exec analyzer_monitor ip link set lo up

    # Sender interface (eth2)
    ip netns exec analyzer_sender ip addr add 10.0.2.10/24 dev eth2
    ip netns exec analyzer_sender ip -6 addr add fd00:2::10/64 dev eth2
    ip netns exec analyzer_sender ip link set eth2 up
    ip netns exec analyzer_sender ip link set lo up

    echo "Ports ready: eth1 in analyzer_monitor, eth2 in analyzer_sender."
}

start_dhcp() {
    if ! ip netns list | grep -q analyzer_monitor || ! ip netns list | grep -q analyzer_sender; then
        setup_ports
    fi
    killall dnsmasq 2>/dev/null

    # DHCP (IPv4 + IPv6) and Router Advertisement for Monitor
    ip netns exec analyzer_monitor dnsmasq --interface=eth1 --bind-interfaces \
      --dhcp-range=10.0.1.20,10.0.1.20,255.255.255.0,12h \
      --dhcp-range=fd00:1::20,fd00:1::20,slaac,64,12h --enable-ra \
      --pid-file=/tmp/dnsmasq_monitor.pid || exit 1

    # DHCP (IPv4 + IPv6) and Router Advertisement for Sender
    ip netns exec analyzer_sender dnsmasq --interface=eth2 --bind-interfaces \
      --dhcp-range=10.0.2.20,10.0.2.20,255.255.255.0,12h \
      --dhcp-range=fd00:2::20,fd00:2::20,slaac,64,12h --enable-ra \
      --pid-file=/tmp/dnsmasq_sender.pid || exit 1

    echo "DHCP and RA active on both ports."
}

case "${1:-all}" in
    ports)  setup_ports ;;
    dhcp)   start_dhcp ;;
    nodhcp) killall dnsmasq 2>/dev/null; echo "DHCP and RA stopped." ;;
    all)    setup_ports; start_dhcp ;;
    *)      echo "Usage: $0 [ports|dhcp|nodhcp]"; exit 2 ;;
esac
