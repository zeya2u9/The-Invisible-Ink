'''
This file contains the logic for checking if the pcaps collected from the android device contain proxy traffic.
The process is as follows:
1. For each pcap in the specified directory:
    a. Check if there are any packets that match the patterns for socks4, socks5 and http/https proxy traffic
    b. Print the results for each pcap with the name of the pcap and the results for each protocol
'''
from scapy.all import *
import struct

pcap_file = "" # path to the pcap file to analyze

def detect_socks4(pkt):
    payload = bytes(pkt[TCP].payload)
    if len(payload) >= 9 and payload[0] == 0x04 and payload[1] == 0x01:  # SOCKS4 version
        dst_port = struct.unpack('>H', payload[2:4])[0]
        dst_ip = '.'.join(map(str, payload[4:8]))
        return f"SOCKS4 detected: {dst_ip}:{dst_port}"
    return None

# Function to detect SOCKS5
def detect_socks5(pkt):
    payload = bytes(pkt[TCP].payload)
    if len(payload) >= 2 and payload[0] == 0x05 and payload[1] == 0x01:  # SOCKS5 version
        dst_ip = pkt[IP].dst
        dst_port = pkt[TCP].dport
        # print(pkt)
        return f"SOCKS5 detected: {dst_ip}:{dst_port}"
    return None

# Function to detect HTTP/HTTPS proxy traffic
def detect_http_https(pkt):
    payload = bytes(pkt[TCP].payload).decode('utf-8', errors='ignore')
    if "CONNECT" in payload:
        return f"HTTP/HTTPS proxy detected: {pkt[IP].dst}"
    return None

def detect_proxy(pcap_file):
    pkts = rdpcap(pcap_file)
    for pkt in pkts:
        if pkt.haslayer(TCP) and pkt.haslayer(IP):
            socks4_result = detect_socks4(pkt)
            socks5_result = detect_socks5(pkt)
            http_https_result = detect_http_https(pkt)
            
            if socks4_result:
                print(f"{pcap_file}: {socks4_result}")
            if socks5_result:
                print(f"{pcap_file}: {socks5_result}")
            if http_https_result:
                print(f"{pcap_file}: {http_https_result}")

detect_proxy(pcap_file)