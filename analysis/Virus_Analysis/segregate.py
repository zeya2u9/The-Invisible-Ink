'''
This script is used to segregate the VPN and Tor related packages from the list of packages in the blacklist. It uses simple string matching to identify the packages related to VPN and Tor services.
The script reads the list of packages from "vpn_packages.txt", checks for the presence of keywords related to VPN and Tor services, and writes the segregated lists to "vpn_services.txt", "tor_services.txt", and "tor_bridge_services.txt".
'''
blacklist = []
with open("vpn_packages.txt") as f:
	for i in f.readlines():
		blacklist.append(i.strip())
		
tor = ["org.torproject"]
torBridge = ["obfs4",
"shadowsocks",
"lantern"]

vpn_file = open("vpn_services.txt", 'w')
tor_file = open("tor_services.txt", 'w')
tor_bridge_file = open("tor_bridge_services.txt", 'w')

for i in blacklist:
	torFound = False
	torBridgeFound = False
	for j in tor:
		if j.lower() in i.lower():
			torFound = True
			break
	
	for j in torBridge:
		if j.lower() in i.lower():
			torBridgeFound = True
			break
	
	if torFound:
		tor_file.write(i + '\n')
	elif torBridgeFound:
		tor_bridge_file.write(i + '\n')
	else:
		vpn_file.write(i + '\n')
