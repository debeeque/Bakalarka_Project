from scapy.all import *

# Interface and target network configuration
iface = "eth2"
ip_range = "10.0.2.0/24"

print(f"Scanning {ip_range} on {iface}...")

try:
    # Send ARP requests and capture responses
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_range),
                     iface=iface, timeout=2, verbose=False)
    
    print(f"Found {len(ans)} devices:")
    for sent, received in ans:
        print(f"IP: {received.psrc}  MAC: {received.hwsrc}")
        
except Exception as e:
    print(f"Error: {e}")