"""A second, foreign DHCP server for autotest.py: answers every DISCOVER on the interface with an OFFER.

sudo ip netns exec analyzer_sender python3 fake_dhcp.py snd0 [seconds]
Not device code: a bench helper for the "2 servers" case.
"""
import sys
import time

from scapy.layers.dhcp import BOOTP, DHCP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.sendrecv import AsyncSniffer, sendp

MAC, SERVER, OFFER = "02:00:00:00:02:50", "10.0.2.250", "10.0.2.240"
iface = sys.argv[1]
seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 60


def answer(p):
    opts = dict(o[:2] for o in p[DHCP].options if isinstance(o, tuple))
    if opts.get("message-type") != 1:
        return
    reply = (Ether(src=MAC, dst="ff:ff:ff:ff:ff:ff") / IP(src=SERVER, dst="255.255.255.255") /
             UDP(sport=67, dport=68) /
             BOOTP(op=2, xid=p[BOOTP].xid, yiaddr=OFFER, siaddr=SERVER, chaddr=p[BOOTP].chaddr, flags=0x8000) /
             DHCP(options=[("message-type", "offer"), ("server_id", SERVER), ("subnet_mask", "255.255.255.0"),
                           ("router", SERVER), ("lease_time", 600), "end"]))
    sendp(reply, iface=iface, verbose=False)
    print("offered %s to %s" % (OFFER, p[Ether].src), flush=True)


s = AsyncSniffer(iface=iface, filter="udp and dst port 67", prn=answer, store=False,
                 lfilter=lambda p: DHCP in p)
s.start()
time.sleep(seconds)
s.stop()
