import requests
import json
import subprocess
import os
from tqdm import tqdm

endpoint = "https://onionoo.torproject.org/details?search="

def search_endpoint(ip, pcap):
    response = requests.get(endpoint + ip)
    response = response.json()
    if len(response["relays"]) != 0:
        print(f"!!!!HAS TORRRR {pcap}!!!!!!")

pcaps = os.listdir("pcaps")
for pcap in tqdm(pcaps, desc="Processing PCAPs"):
    if not pcap.endswith(".pcap"):
        continue
    pcap_path = os.path.join("pcaps", pcap)
    command = [
        "tshark", 
        "-r", pcap_path,  # Read the pcap file
        "-Y", "tcp.flags.syn==1 && ip.dst && !(ip.dst == 127.0.0.0/8 || ip.dst == 10.0.0.0/8 || ip.dst == 172.16.0.0/12 || ip.dst == 192.168.0.0/16)",  # Filter for TCP SYN packets with non-local destination IPs
        "-T", "fields",  # Output as fields (IP addresses)
        "-e", "ip.dst"  # Extract destination IP addresses
    ]

    output = subprocess.check_output(command)
    output_decoded = output.decode("utf-8")

    unique_ips = sorted(set(output_decoded.splitlines()))

    for ip in unique_ips:
        search_endpoint(ip, pcap)