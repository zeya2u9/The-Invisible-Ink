'''
This file contains the logic for analyzing the pcaps collected from the android device.
The process is as follows:
1. For each pcap in the specified directory:
    a. Check if there are any packets that match the patterns for ipsec, openvpn, sstp and pptp
    b. Save the results in a csv file with the name of the pcap and the results for each protocol
'''
from scapy.all import *
import os
import json
import csv
import re
import pydnsbl

zgrab = "" # path to zgrab binary

ip_checker = pydnsbl.DNSBLIpChecker()

output = open("output.csv", "w")
csv_writer = csv.writer(output)

csv_writer.writerow(["pcap", "ipsec", "openvpn", "sstp", "pptp"])

ipsecFile = "ipsec.txt"
openvpnFile = "openvpn.txt"
sstpFile = "sstp.txt"
pptpFile = "pptp.txt"
ipsec = "ipsec.txt"

ipsec_initiator_spi = "080fd6f205d3879d"
ipsec_payload_7cs = "080fd6f205d3879d00000000000000000110020000000000000001980d0000d40000000100000001000000c801010005030000280101000080010007800e0100800200028004001480030001800b0001000c000400007080030000280201000080010007800e0080800200028004001380030001800b0001000c000400007080030000280301000080010007800e0100800200028004000e80030001800b0001000c000400007080030000240401000080010005800200028004000e80030001800b0001000c000400007080000000240501000080010005800200028004000280030001800b0001000c0004000070800d00001801528bbbc00696121849ab9a1c5b2a51000000010d0000181e2b516905991c7d7c96fcbfb587e461000000090d0000144a131c81070358455c5728f20e95452f0d00001490cb80913ebb696e086381b5ec427b1f0d0000144048b7d56ebce88525e7de7f00d6c2d30d000014fb1de3cdf341b7ea16b7e5be0855f1200d00001426244d38eddb61b3172a36e3d0cfb81900000014e3a5966a76379fe707228231e5ce8652"

openvpn_no_tls_pattern = re.compile("00([a-f0-9]{2})(40|10)([a-f0-9]{16})((0000000000)|(01([a-f0-9]{24})00000000))")

ip_to_domain = dict()

def check_ipsec(file, port):
    os.system(f"sudo zmap --probe-module=udp -f saddr,data -p {port} -o res.csv --allowlist-file={file}")

    with open("res.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[1].startswith(ipsec_initiator_spi):
                if row[1] != ipsec_payload_7cs:
                    return True
                    
    os.remove("res.csv")
    
    return False

def check_openvpn_udp(file, port):
    os.system(f"sudo zmap --probe-module=udp -f saddr,data,success -p {port} -o res.csv --allowlist-file={file}")

    with open("res.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            if bool(row[2]) and openvpn_no_tls_pattern.match(row[1]):
                return True
                
    os.remove("res.csv")

    return False

def check_ipsec_ipv6(file, port, src):
    os.system(f"sudo zmap --probe-module=ipv6_udp -f saddr,data -p {port} -o res.csv --ipv6-target-file={file} --ipv6-source-ip={src}")

    with open("res.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[1].startswith(ipsec_initiator_spi):
                if row[1] != ipsec_payload_7cs:
                    return True
                    
    os.remove("res.csv")
    
    return False

def check_openvpn_udp_ipv6(file, port, src):
    os.system(f"sudo zmap --probe-module=ipv6_udp -f saddr,data,success -p {port} -o res.csv --ipv6-target-file={file} --ipv6-source-ip={src}")

    with open("res.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            if bool(row[2]) and openvpn_no_tls_pattern.match(row[1]):
                return True
                
    os.remove("res.csv")

    return False

pcaps = os.listdir()

for pcap in pcaps:
    if not pcap.endswith('.pcap'):
        continue

    ipsec = False
    openvpn = False
    sstp = False
    pptp = False

    ipsecLinks = set()
    openvpnUDPLinks = set()
    openvpnLinks = set()
    sstpLinks = set()
    pptpLinks = set()

    tcpLinks = dict()
    udpLinks = dict()

    udpLinksIPv6 = dict()

    cur = rdpcap(pcap)
    for pkt in cur:
        if IP in pkt:
            ip_dst = pkt[IP].dst

            if ip_checker.check(ip_dst).blacklisted:
                continue

            if UDP in pkt:
                port = pkt[UDP].dport
                
                if port not in udpLinks:
                    udpLinks[port] = []
                
                udpLinks[port].append(ip_dst + "/32")

            elif TCP in pkt:
                port = pkt[TCP].dport

                if port == 1723:
                    pptpLinks.add(ip_dst)

                if port not in tcpLinks:
                    tcpLinks[port] = []
                	
                tcpLinks[port].append(ip_dst)

        elif IPv6 in pkt:
            ip_dst = pkt[IPv6].dst

            if ip_checker.check(ip_dst).blacklisted:
                continue

            if UDP in pkt:
                port = pkt[UDP].dport
                
                if port not in udpLinksIPv6:
                    udpLinksIPv6[port] = dict()

                src = pkt[IPv6].src

                if src not in udpLinksIPv6[port]:
                    udpLinksIPv6[port][src] = []
                
                udpLinksIPv6[port][src].append(ip_dst)

            elif TCP in pkt:
                port = pkt[TCP].dport

                if port == 1723:
                    pptpLinks.add(ip_dst)

                if port not in tcpLinks:
                    tcpLinks[port] = []
                	
                tcpLinks[port].append(ip_dst)

        if pkt.haslayer(DNS):
            dns = pkt[DNS]

            if dns.qr == 1:
                for i in range(dns.ancount):
                    ans = dns.an[i]
                    if ans.type in [1, 28]:  # Type 1 is an A record (IPv4) type 28 is AAAA record (IPv6) 5 is CNAME
                        domain = ans.rrname.decode('utf-8')
                        ip = ans.rdata
                        ip_to_domain[ip].append(domain)

    for port, links in udpLinks.items():
        if not ipsec:
            with open(ipsecFile, 'w') as file:
                file.write("\n".join(links))
            ipsec = check_ipsec(ipsecFile, port)
            os.remove(ipsecFile)

        if not openvpn:
            with open(openvpnFile, 'w') as file:
                file.write("\n".join(links))
            openvpn = check_openvpn_udp(openvpnFile, port)
            os.remove(openvpnFile)

    for port, src_links in udpLinksIPv6.items():
        for src, links in src_links.items():
            if not ipsec:
                with open(ipsecFile, 'w') as file:
                    file.write("\n".join(links))
                ipsec = check_ipsec_ipv6(ipsecFile, port, src)
                os.remove(ipsecFile)

            if not openvpn:
                with open(openvpnFile, 'w') as file:
                    file.write("\n".join(links))
                openvpn = check_openvpn_udp_ipv6(openvpnFile, port, src)
                os.remove(openvpnFile)

    for port, links in tcpLinks.items():
        if not openvpn:
            with open(openvpnFile, 'w') as file:
                file.write("\n".join(links))
            try:
                os.system(f"{zgrab} tcp --protocol openvpn --port {port} -o 'out.txt' -f '{openvpnFile}'")
                with open("out.txt") as f:
                    lines = f.readlines()
                    for line in lines:
                        data = json.loads(line)
                        if data["data"]["tcp"]["status"] == "success" and "response" in data["data"]["tcp"]["result"] and openvpn_no_tls_pattern.match(data["data"]["tcp"]["result"]["response"]):
                            openvpn = True
                            break

            except Exception as e:
                print(str(e), "\n\n\nopenvpn\n\n\n")
                
            finally:
                os.remove(openvpnFile)

        if not sstp:
            with open(sstpFile, 'w') as file:
                file.write("\n".join(links))
            try:
                os.system(f"{zgrab} sstp --port {port} -o 'out.txt' -f '{sstpFile}'")
                with open("out.txt") as f:
                    lines = f.readlines()
                    for line in lines:
                        data = json.loads(line)
                        if data["data"]["sstp"]["status"] == "success":
                            if "result" in data["data"]["sstp"] and "status" in data["data"]["sstp"]["result"]:
                                if '200' in data['data']['sstp']['result']['status'] or 'OK' in data['data']['sstp']['result']['status']:
                                    sstp = True
                                    break

            except Exception as e:
                print(str(e), "\n\n\nsstp\n\n\n")
                
            finally:
                os.remove(sstpFile)


    if not pptp and pptpLinks:
        with open(pptpFile, 'w') as file:
            file.write("\n".join(pptpLinks))
        try:
            os.system(f"{zgrab} tcp --protocol pptp --port 1723 -o 'out.txt' -f '{pptpFile}'")
            with open("out.txt") as f:
                lines = f.readlines()
                for line in lines:
                    data = json.loads(line)
                    if data["data"]["tcp"]["status"] == "success":
                        pptp = True
                        break

        except Exception as e:
            print(str(e), "\n\n\npptp\n\n\n")

        finally:
            os.remove(pptpFile)


    if "out.txt" in os.listdir():
        os.remove("out.txt")

    csv_writer.writerow([pcap, ipsec, openvpn, sstp, pptp])


output.close()

