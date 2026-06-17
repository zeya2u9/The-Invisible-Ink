'''
This file contains the logic for checking if the pcaps collected from the android device contain tor traffic.
The process is as follows:
1. Get the list of tor guards from the tor network status
2. For each pcap in the specified directory:
    a. Check if there are any packets that have a destination IP that matches any of the tor guards
    b. Save the results in a csv file with the name of the pcap and whether it contains tor traffic or not
'''
import stem.control
from scapy.all import *
import os
import csv

output = open("tor.csv", "w")
writer = csv.writer(output)

writer.writerow(["pcap", "tor"])

port = 9051

guards = []

with stem.control.Controller.from_port(port=port) as controller:
    controller.authenticate()

    for desc in controller.get_network_statuses():
        info = controller.get_info('ns/id/' + desc.fingerprint)
        if (info.find('Guard') > -1):
            guards.append(desc.address)


for file in os.listdir():
    tor = False
    if not file.endswith(".pcap"):
        continue

    cur = rdpcap(file)

    for pkt in cur:
        if IP in pkt:
            dst = pkt[IP].dst
            if dst in guards:
                tor = True

    writer.writerow([file, tor])

output.close()
