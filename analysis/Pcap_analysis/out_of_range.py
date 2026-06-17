'''
This file contains the logic for finding the IPv4 addresses that are not covered by the CIDR ranges in the routes string.
The process is as follows:
1. Extract the CIDR ranges from the routes string
2. Union the CIDR ranges to combine overlapping and adjacent ranges
3. Find the missing IPv4 addresses that are not covered by the unionized ranges
4. Generate CIDR blocks for the missing ranges
5. Remove the IPv6 ranges from the unionized ranges
6. Print the missing CIDR blocks
'''
import ipaddress

routes = " 0.0.0.0/5 -> 0.0.0.0 tun0 mtu 0,8.0.0.0/7 -> 0.0.0.0 tun0 mtu 0,11.0.0.0/8 -> 0.0.0.0 tun0 mtu 0,12.0.0.0/6 -> 0.0.0.0 tun0 mtu 0,16.0.0.0/4 -> 0.0.0.0 tun0 mtu 0,32.0.0.0/3 -> 0.0.0.0 tun0 mtu 0,64.0.0.0/9 -> 0.0.0.0 tun0 mtu 0,64.128.0.0/13 -> 0.0.0.0 tun0 mtu 0,64.136.0.0/16 -> 0.0.0.0 tun0 mtu 0,64.137.0.0/19 -> 0.0.0.0 tun0 mtu 0,64.137.32.0/21 -> 0.0.0.0 tun0 mtu 0,64.137.40.0/23 -> 0.0.0.0 tun0 mtu 0,64.137.42.0/26 -> 0.0.0.0 tun0 mtu 0,64.137.42.64/27 -> 0.0.0.0 tun0 mtu 0,64.137.42.96/28 -> 0.0.0.0 tun0 mtu 0,64.137.42.113/32 -> 0.0.0.0 tun0 mtu 0,64.137.42.114/31 -> 0.0.0.0 tun0 mtu 0,64.137.42.116/30 -> 0.0.0.0 tun0 mtu 0,64.137.42.120/29 -> 0.0.0.0 tun0 mtu 0,64.137.42.128/25 -> 0.0.0.0 tun0 mtu 0,64.137.43.0/24 -> 0.0.0.0 tun0 mtu 0,64.137.44.0/22 -> 0.0.0.0 tun0 mtu 0,64.137.48.0/20 -> 0.0.0.0 tun0 mtu 0,64.137.64.0/18 -> 0.0.0.0 tun0 mtu 0,64.137.128.0/17 -> 0.0.0.0 tun0 mtu 0,64.138.0.0/15 -> 0.0.0.0 tun0 mtu 0,64.140.0.0/14 -> 0.0.0.0 tun0 mtu 0,64.144.0.0/12 -> 0.0.0.0 tun0 mtu 0,64.160.0.0/11 -> 0.0.0.0 tun0 mtu 0,64.192.0.0/10 -> 0.0.0.0 tun0 mtu 0,65.0.0.0/8 -> 0.0.0.0 tun0 mtu 0,66.0.0.0/7 -> 0.0.0.0 tun0 mtu 0,68.0.0.0/6 -> 0.0.0.0 tun0 mtu 0,72.0.0.0/5 -> 0.0.0.0 tun0 mtu 0,80.0.0.0/4 -> 0.0.0.0 tun0 mtu 0,96.0.0.0/3 -> 0.0.0.0 tun0 mtu 0,128.0.0.0/3 -> 0.0.0.0 tun0 mtu 0,160.0.0.0/5 -> 0.0.0.0 tun0 mtu 0,168.0.0.0/6 -> 0.0.0.0 tun0 mtu 0,172.0.0.0/12 -> 0.0.0.0 tun0 mtu 0,172.32.0.0/11 -> 0.0.0.0 tun0 mtu 0,172.64.0.0/10 -> 0.0.0.0 tun0 mtu 0,172.128.0.0/9 -> 0.0.0.0 tun0 mtu 0,173.0.0.0/8 -> 0.0.0.0 tun0 mtu 0,174.0.0.0/7 -> 0.0.0.0 tun0 mtu 0,176.0.0.0/4 -> 0.0.0.0 tun0 mtu 0,192.0.0.0/9 -> 0.0.0.0 tun0 mtu 0,192.128.0.0/11 -> 0.0.0.0 tun0 mtu 0,192.160.0.0/13 -> 0.0.0.0 tun0 mtu 0,192.169.0.0/16 -> 0.0.0.0 tun0 mtu 0,192.170.0.0/15 -> 0.0.0.0 tun0 mtu 0,192.172.0.0/14 -> 0.0.0.0 tun0 mtu 0,192.176.0.0/12 -> 0.0.0.0 tun0 mtu 0,192.192.0.0/10 -> 0.0.0.0 tun0 mtu 0,193.0.0.0/8 -> 0.0.0.0 tun0 mtu 0,194.0.0.0/7 -> 0.0.0.0 tun0 mtu 0,196.0.0.0/6 -> 0.0.0.0 tun0 mtu 0,200.0.0.0/5 -> 0.0.0.0 tun0 mtu 0,208.0.0.0/4 -> 0.0.0.0 tun0 mtu 0,224.0.0.0/3 -> 0.0.0.0 tun0 mtu 0,::/0 unreachable mtu 0,172.16.0.0/12 -> 0.0.0.0 tun0 mtu 0 "

def extract_cidr_ranges(routes):
    """
    Extracts all CIDR ranges from the routes string.
    """
    cidr_ranges = []
    for entry in routes.split(","):
        parts = entry.strip().split(" ")
        if len(parts) > 0 and "/" in parts[0]:  # Check if the first part is a CIDR range
            cidr = parts[0]
            try:
                # Validate and add CIDR
                cidr_ranges.append(ipaddress.ip_network(cidr))
            except ValueError:
                pass  # Skip invalid CIDRs
    return cidr_ranges

def union_cidr_ranges(cidr_ranges):
    """
    Combines overlapping and adjacent CIDR ranges.
    """
    sorted_ranges = sorted(cidr_ranges, key=lambda x: (x.network_address, x.prefixlen))
    merged_ranges = []
    for current in sorted_ranges:
        if not merged_ranges:
            merged_ranges.append(current)
        else:
            last = merged_ranges[-1]
            # Check if current range overlaps or is adjacent to the last range
            if last.overlaps(current) or last.network_address + last.num_addresses == current.network_address:
                # Merge the ranges
                merged_ranges[-1] = last.supernet(new_prefix=min(last.prefixlen, current.prefixlen))
            else:
                merged_ranges.append(current)
    return merged_ranges

def find_missing_ips(unionized_ranges):
    """
    Identifies the IPv4 addresses not covered by the unionized ranges.
    """
    all_ips = ipaddress.ip_network("0.0.0.0/0")  # Full IPv4 range
    covered_ips = [ip for cidr in unionized_ranges for ip in cidr]
    missing_ips = [ip for ip in all_ips if ip not in covered_ips]
    return missing_ips

def generate_cidr_from_range(start_ip, end_ip):
    """
    Given a start IP and an end IP, generate the corresponding CIDR blocks that cover the IP range.
    :param start_ip: The starting IP address (as a string)
    :param end_ip: The ending IP address (as a string)
    :return: List of CIDR blocks covering the IP range
    """
    start = int(ipaddress.IPv4Address(start_ip))
    end = int(ipaddress.IPv4Address(end_ip))
    cidr_blocks = []
    last_start = None
    while start <= end:
        # Find the largest block size that fits the range
        max_size = 32
        # print(last_start, start, end)
        if start == last_start:
            cidr_blocks.extend(generate_one_cidr_from_range(start, end))
            break
        last_start = start
        while max_size > 0:
            # Calculate the maximum block that fits into the remaining range
            network_size = 32 - (start.bit_length() - max_size)
            mask = 32 - network_size
            network_end = start | (1 << network_size) - 1
            if network_end <= end:
                cidr_blocks.append(str(ipaddress.IPv4Network((start, mask), strict=False)))
                start = network_end + 1
                break
            max_size -= 1
    return cidr_blocks


def generate_one_cidr_from_range(start_ip, end_ip):
    """
    Given a start IP and an end IP, generate the corresponding CIDR blocks that cover the IP range.
    :param start_ip: The starting IP address (as a string)
    :param end_ip: The ending IP address (as a string)
    :return: List of CIDR blocks covering the IP range
    """
    start = int(ipaddress.IPv4Address(start_ip))
    end = int(ipaddress.IPv4Address(end_ip))
    cidr_blocks = []
    while start <= end:
        # Try to find the largest CIDR block
        current_start = start
        for mask in range(32, -1, -1):
            network = current_start & (0xFFFFFFFF << (32 - mask))  # Mask the start IP
            network_end = network | ((1 << (32 - mask)) - 1)  # Get the last IP of the network
            # Check if this network fits within the range
            if network_end <= end:
                cidr_blocks.append(str(ipaddress.IPv4Network((network, mask), strict=False)))
                start = network_end + 1
                break
    return cidr_blocks

def find_missing_ranges(sorted_ranges):
    missings_ranges = []
    for i in range(len(sorted_ranges) - 1):
        if sorted_ranges[i].broadcast_address + 1 != sorted_ranges[i + 1].network_address:
            for missing_range in generate_cidr_from_range(sorted_ranges[i].broadcast_address + 1, sorted_ranges[i + 1].network_address - 1):
                missings_ranges.append(ipaddress.ip_network(missing_range))
    return missings_ranges

def remove_ipv6(cidr_ranges):
    """
    Removes IPv6 ranges from the unionized ranges.
    """
    return [cidr for cidr in cidr_ranges if cidr.version == 4]

cidr_ranges = extract_cidr_ranges(routes)
cidr_ranges = remove_ipv6(cidr_ranges)
cidr_ranges = sorted(cidr_ranges, key=lambda x: (x.network_address, x.prefixlen))

print(find_missing_ranges(cidr_ranges))


routes_warp = "0.0.0.0/0 -> 0.0.0.0 tun0 mtu 0,::/0 -> :: tun0 mtu 0,172.16.0.2/32 -> 0.0.0.0 tun0 mtu 0,2606:4700:110:8557:d8d5:a030:a338:3332/128 -> :: tun0 mtu 0"
routes_socks5_v4 = "0.0.0.0/0 -> 0.0.0.0 tun0 mtu 0,::/0 -> :: tun0 mtu 0,26.26.26.0/24 -> 0.0.0.0 tun0 mtu 0"
routes_socks5_v6 = "0.0.0.0/0 -> 0.0.0.0 tun0 mtu 0,::/0 -> :: tun0 mtu 0,26.26.26.0/24 -> 0.0.0.0 tun0 mtu 0,da26:2626::/126 -> :: tun0 mtu 0"