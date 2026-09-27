import sys
import time

from scapy.all import (ARP, DHCP, BOOTP, DNS, DNSQR, DNSRR, Dot1Q, Ether, ICMP, ICMPv6DestUnreach,
                       ICMPv6EchoReply, ICMPv6EchoRequest, ICMPv6MLReport2, ICMPv6MLDMultAddrRec,
                       ICMPv6ND_NA, ICMPv6ND_NS, ICMPv6ND_RA, ICMPv6ND_RS, ICMPv6NDOptDstLLAddr,
                       ICMPv6NDOptMTU, ICMPv6NDOptPrefixInfo, ICMPv6NDOptRDNSS, ICMPv6NDOptSrcLLAddr,
                       ICMPv6PacketTooBig, IP, IPv6, IPv6ExtHdrFragment, IPv6ExtHdrHopByHop, RouterAlert,
                       Raw, TCP, UDP, sendp)
from scapy.layers.dhcp6 import DHCP6_Solicit, DHCP6OptClientId, DHCP6OptElapsedTime, DUID_LL

iface = sys.argv[1]
SRC = "00:e0:4c:68:02:23"
DST = "00:e0:4c:68:02:01"
LL_S = "fe80::2e0:4cff:fe68:223"
LL_D = "fe80::2e0:4cff:fe68:201"

f = []
e = Ether(src=SRC, dst=DST)
f.append(e / IP(src="10.0.2.10", dst="10.0.1.10", ttl=61, id=0x1234) / ICMP(type=8, id=7, seq=1) / Raw(b"x" * 32))
f.append(e / IP(src="10.0.1.10", dst="10.0.2.10", ttl=64) / ICMP(type=0, id=7, seq=1) / Raw(b"y" * 32))
f.append(e / IP(src="10.0.2.10", dst="10.0.1.10") / UDP(sport=40000, dport=53) /
         DNS(id=0xabcd, rd=1, qd=DNSQR(qname="analyzer.test", qtype="AAAA")))
f.append(e / IP(src="10.0.1.10", dst="10.0.2.10") / UDP(sport=53, dport=40000) /
         DNS(id=0xabcd, qr=1, qd=DNSQR(qname="analyzer.test", qtype="A"),
             an=DNSRR(rrname="analyzer.test", rdata="10.0.1.10")))
f.append(Ether(src=SRC, dst="ff:ff:ff:ff:ff:ff") / IP(src="0.0.0.0", dst="255.255.255.255") /
         UDP(sport=68, dport=67) / BOOTP(chaddr=bytes.fromhex("00e04c680223") + b"\0" * 10, xid=0x11223344) /
         DHCP(options=[("message-type", "discover"), "end"]))
f.append(e / IP(src="10.0.1.10", dst="10.0.2.10") / UDP(sport=67, dport=68) /
         BOOTP(op=2, yiaddr="10.0.2.20", chaddr=bytes.fromhex("00e04c680223") + b"\0" * 10, xid=0x11223344) /
         DHCP(options=[("message-type", "offer"), "end"]))
f.append(e / IP(src="10.0.2.10", dst="10.0.1.10") / TCP(sport=12345, dport=80, flags="S", seq=1000, window=64240))
f.append(e / IP(src="10.0.1.10", dst="10.0.2.10") / TCP(sport=80, dport=12345, flags="SA", seq=5000, ack=1001, window=65160))
f.append(e / IP(src="10.0.2.10", dst="10.0.1.10", flags="MF", frag=0) / UDP(sport=5000, dport=5001) / Raw(b"a" * 64))
f.append(e / IP(src="10.0.2.10", dst="10.0.1.10", frag=9, proto=17) / Raw(b"b" * 40))
f.append(Ether(src=SRC, dst="ff:ff:ff:ff:ff:ff") / ARP(op=1, hwsrc=SRC, psrc="10.0.2.10", pdst="10.0.1.10"))
f.append(e / ARP(op=2, hwsrc=SRC, psrc="10.0.2.10", hwdst=DST, pdst="10.0.1.10"))
f.append(e / IPv6(src=LL_S, dst=LL_D) / ICMPv6EchoRequest(id=9, seq=3) / Raw(b"z" * 16))
f.append(e / IPv6(src=LL_D, dst=LL_S) / ICMPv6EchoReply(id=9, seq=3) / Raw(b"z" * 16))
f.append(Ether(src=SRC, dst="33:33:00:00:00:02") / IPv6(src=LL_S, dst="ff02::2", hlim=255) /
         ICMPv6ND_RS() / ICMPv6NDOptSrcLLAddr(lladdr=SRC))
f.append(Ether(src=SRC, dst="33:33:00:00:00:01") / IPv6(src=LL_S, dst="ff02::1", hlim=255) /
         ICMPv6ND_RA(chlim=64, M=1, O=0, prf=1, routerlifetime=1800, reachabletime=30000, retranstimer=1000) /
         ICMPv6NDOptSrcLLAddr(lladdr=SRC) / ICMPv6NDOptMTU(mtu=1500) /
         ICMPv6NDOptPrefixInfo(prefix="fd00:2::", prefixlen=64, L=1, A=1, validlifetime=43200, preferredlifetime=14400) /
         ICMPv6NDOptRDNSS(dns=["fd00:2::10"], lifetime=600))
f.append(Ether(src=SRC, dst="33:33:00:00:00:01") / IPv6(src=LL_S, dst="ff02::1", hlim=64) /
         ICMPv6ND_RA(chlim=0, M=0, O=1, prf=3, routerlifetime=0) /
         ICMPv6NDOptPrefixInfo(prefix="2001:db8:1::", prefixlen=48, L=0, A=1, validlifetime=0xFFFFFFFF, preferredlifetime=0xFFFFFFFF))
f.append(Ether(src=SRC, dst="33:33:ff:68:02:01") / IPv6(src=LL_S, dst="ff02::1:ff68:201", hlim=255) /
         ICMPv6ND_NS(tgt=LL_D) / ICMPv6NDOptSrcLLAddr(lladdr=SRC))
f.append(e / IPv6(src=LL_D, dst=LL_S, hlim=255) / ICMPv6ND_NA(tgt=LL_D, R=0, S=1, O=1) / ICMPv6NDOptDstLLAddr(lladdr=DST))
f.append(Ether(src=SRC, dst="33:33:00:00:00:16") / IPv6(src=LL_S, dst="ff02::16", hlim=1) /
         IPv6ExtHdrHopByHop(options=[RouterAlert()]) /
         ICMPv6MLReport2(records=[ICMPv6MLDMultAddrRec(rtype=4, dst="ff02::1:ff68:223")]))
f.append(Ether(src=SRC, dst="33:33:00:01:00:02") / IPv6(src=LL_S, dst="ff02::1:2") / UDP(sport=546, dport=547) /
         DHCP6_Solicit(trid=0x123456) / DHCP6OptClientId(duid=DUID_LL(lladdr=SRC)) / DHCP6OptElapsedTime())
f.append(e / IPv6(src="fd00:2::10", dst="fd00:1::10") / TCP(sport=33000, dport=443, flags="S", seq=42, window=64800))
f.append(e / IPv6(src="fd00:1::10", dst="fd00:2::10", hlim=64) / ICMPv6PacketTooBig(mtu=1400) /
         IPv6(src="fd00:2::10", dst="fd00:1::10") / UDP(sport=1, dport=2) / Raw(b"q" * 40))
f.append(e / IPv6(src="fd00:1::10", dst="fd00:2::10") / ICMPv6DestUnreach(code=4) /
         IPv6(src="fd00:2::10", dst="fd00:1::10") / UDP(sport=3, dport=4))
f.append(e / IPv6(src=LL_S, dst=LL_D) / IPv6ExtHdrFragment(id=77, offset=0, m=1) / UDP(sport=6000, dport=6001) / Raw(b"f" * 48))
f.append(e / Dot1Q(vlan=100, prio=5) / IP(src="10.0.2.10", dst="10.0.1.10") / ICMP(type=8, id=1, seq=9))
f.append(Ether(src=SRC, dst="01:80:c2:00:00:0e", type=0x88CC) / Raw(bytes.fromhex("0207046c6c6470") + b"\0" * 40))

for p in f:
    sendp(p, iface=iface, verbose=0)
    time.sleep(0.05)
print("sent", len(f))
