"""Test frames for l2_listen.py on the loop: CDP like a Cisco switch, an RSTP BPDU and a LACPDU.

sudo ip netns exec analyzer_sender python3 l2_test_send.py snd0
Not device code: a bench helper, not part of the thesis appendix.
"""
import sys

from scapy.contrib.cdp import (CDPAddrRecordIPv4, CDPMsgAddr, CDPMsgDeviceID, CDPMsgNativeVLAN, CDPMsgPlatform,
                               CDPMsgPortID, CDPMsgSoftwareVersion, CDPv2_HDR)
from scapy.layers.l2 import LLC, SNAP, STP, Dot3, Ether
from scapy.packet import Raw
from scapy.sendrecv import sendp

FAKE = "00:1b:2b:aa:bb:05"
iface = sys.argv[1]

cdp = (Dot3(dst="01:00:0c:cc:cc:cc", src=FAKE) / LLC(dsap=0xAA, ssap=0xAA, ctrl=3) / SNAP(OUI=0x0C, code=0x2000) /
       CDPv2_HDR(ttl=180, msg=[CDPMsgDeviceID(val=b"TestSwitch.lab"),
                               CDPMsgSoftwareVersion(val=b"Cisco IOS Software, C2960 15.0(2)SE11"),
                               CDPMsgPlatform(val=b"cisco WS-C2960-24TT-L"),
                               CDPMsgAddr(addr=[CDPAddrRecordIPv4(addr="192.168.1.2")]),
                               CDPMsgPortID(iface=b"FastEthernet0/5"),
                               CDPMsgNativeVLAN(vlan=10)]))
stp = (Dot3(dst="01:80:c2:00:00:00", src=FAKE) / LLC(dsap=0x42, ssap=0x42, ctrl=3) /
       STP(version=2, bpdutype=2, rootid=24576, rootmac="00:1b:2b:aa:bb:00", bridgeid=32768, bridgemac=FAKE))
lacp = Ether(dst="01:80:c2:00:00:02", src=FAKE, type=0x8809) / Raw(b"\x01\x01" + b"\x00" * 108)

sendp([cdp, stp, lacp], iface=iface, verbose=False)
print("sent CDP, RSTP BPDU and LACPDU from %s on %s" % (FAKE, iface))
