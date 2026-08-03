#!/bin/bash

# Terminate existing services and clean up namespaces
killall dnsmasq 2>/dev/null
ip netns delete analyzer_monitor 2>/dev/null
ip netns delete analyzer_sender 2>/dev/null

# Deleting a namespace returns its physical interfaces asynchronously
wait_for_iface() {
    for _ in $(seq 1 50); do
        [ -e "/sys/class/net/$1" ] && return 0
        sleep 0.1
    done
    echo "Error: interface $1 did not return to the default namespace"
    return 1
}

wait_for_iface eth1 || exit 1
wait_for_iface eth2 || exit 1

# Create new isolated network namespaces
ip netns add analyzer_monitor
ip netns add analyzer_sender

# Assign physical interfaces to namespaces
ip link set dev eth1 netns analyzer_monitor
ip link set dev eth2 netns analyzer_sender

# ==========================================
# Configuration: Monitor Interface (eth1)
# ==========================================
ip netns exec analyzer_monitor ip addr add 10.0.1.10/24 dev eth1
ip netns exec analyzer_monitor ip -6 addr add fd00:1::10/64 dev eth1
ip netns exec analyzer_monitor ip link set eth1 up
ip netns exec analyzer_monitor ip link set lo up

# Initialize DHCP (IPv4 + IPv6) for Monitor
ip netns exec analyzer_monitor dnsmasq --interface=eth1 --bind-interfaces \
  --dhcp-range=10.0.1.20,10.0.1.20,255.255.255.0,12h \
  --dhcp-range=fd00:1::20,fd00:1::20,slaac,64,12h --enable-ra \
  --pid-file=/tmp/dnsmasq_monitor.pid

# ==========================================
# Configuration: Sender Interface (eth2)
# ==========================================
ip netns exec analyzer_sender ip addr add 10.0.2.10/24 dev eth2
ip netns exec analyzer_sender ip -6 addr add fd00:2::10/64 dev eth2
ip netns exec analyzer_sender ip link set eth2 up
ip netns exec analyzer_sender ip link set lo up

# Initialize DHCP (IPv4 + IPv6) for Sender
ip netns exec analyzer_sender dnsmasq --interface=eth2 --bind-interfaces \
  --dhcp-range=10.0.2.20,10.0.2.20,255.255.255.0,12h \
  --dhcp-range=fd00:2::20,fd00:2::20,slaac,64,12h --enable-ra \
  --pid-file=/tmp/dnsmasq_sender.pid

echo "Network setup complete. IPv4 and IPv6 isolated modes active."