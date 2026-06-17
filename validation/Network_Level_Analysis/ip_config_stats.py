import os
import re
from tqdm import tqdm

regex = r"""
\b(?:
  # IPv4: match 4 groups of numbers from 0-255 separated by dots
  (?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)
|
  # IPv6: match various forms of IPv6 addresses including shorthand
  (?:
    (?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}         |  # 1:2:3:4:5:6:7:8
    (?:[A-Fa-f0-9]{1,4}:){1,7}:                      |  # 1:: or 1:2:3:4:5:6:7::
    (?:[A-Fa-f0-9]{1,4}:){1,6}:[A-Fa-f0-9]{1,4}      |  # 1::8 or 1:2:3:4:5:6::8
    (?:[A-Fa-f0-9]{1,4}:){1,5}(?::[A-Fa-f0-9]{1,4}){1,2} |  # 1::7:8 or 1:2:3:4:5::7:8
    (?:[A-Fa-f0-9]{1,4}:){1,4}(?::[A-Fa-f0-9]{1,4}){1,3} |  # 1::6:7:8 or 1:2:3:4::6:7:8
    (?:[A-Fa-f0-9]{1,4}:){1,3}(?::[A-Fa-f0-9]{1,4}){1,4} |  # 1::5:6:7:8 or 1:2:3::5:6:7:8
    (?:[A-Fa-f0-9]{1,4}:){1,2}(?::[A-Fa-f0-9]{1,4}){1,5} |  # 1::4:5:6:7:8 or 1:2::4:5:6:7:8
    [A-Fa-f0-9]{1,4}:(?:(?::[A-Fa-f0-9]{1,4}){1,6})     |  # 1::3:4:5:6:7:8 (with leading group)
    :(?:(?::[A-Fa-f0-9]{1,4}){1,7}|:)                     # ::2:3:4:5:6:7:8 or :: (all zero)
  )
)\b
"""

default_ip = "103.94.108.78"

pattern = re.compile(regex, re.VERBOSE | re.IGNORECASE)

ip_config_dir = "/home/nsl407/COMEX/Data/ip_stat"

dir_files = os.listdir(ip_config_dir)
hashes = set([i.split("-")[0] for i in dir_files])

for hash in tqdm(hashes):
    for i in range(1, 6):
        filename = f"{hash}-{i}.txt"

        if filename not in dir_files:
            # print(f"Missing: {filename}")
            break

        with open(os.path.join(ip_config_dir, filename), "r") as f:
            lines = f.readlines()
            if not lines:
                # print(f"Empty: {filename}")
                break
            
            line = lines[-1].strip()

            ip_match = pattern.search(line)

            if ip_match:
                # print(f"{filename}: {ip_match.group()}")
                if ip_match.group() != default_ip:
                    print(f"{filename}: {ip_match.group()}")

