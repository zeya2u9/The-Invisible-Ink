import os
import tqdm

data_dir = "./data"

with open("proxy_packages.txt", "r") as f:
    lines = f.readlines()

proxy_libraries = [line.strip().split(',')[0] for line in lines]

tor_bridge_libraries = set([
    # "libtun2socks.so",
    "libsnowflake.so",
    "libobfs4proxy.so",
    "libwebtunnel.so",
    "libconjure.so"
])

tor_services = ["org.torproject", "libtor.so", "torrc"]
vpn_check = "setting state=connecting"
vpn_ps_check = "com.android.vpndialog"

libtun2sock_count = 0

check_hashes = set([i.split(".")[0].split("-")[0] for i in os.listdir(os.path.join(data_dir, "logcat"))])

tor_validated = set()
vpn_validated = set()
proxy_validated = set()
pt_validated = set()


for hash in tqdm.tqdm(check_hashes):
    try:
        if os.path.exists(os.path.join(data_dir, "logcat", f"{hash}.log")):
            logcat_file = os.path.join(data_dir, "logcat", f"{hash}.log")
        elif os.path.exists(os.path.join(data_dir, "logcat", f"{hash}-5.log")):
            logcat_file = os.path.join(data_dir, "logcat", f"{hash}-5.log")
        
        else:
            print(f"Could not find logcat file for {hash}")
            continue

        with open(logcat_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.lower()
                if vpn_check in line:
                    vpn_validated.add(hash)
                for lib in tor_bridge_libraries:
                    if lib in line:
                        tor_validated.add(hash)
                for lib in proxy_libraries:
                    if lib in line:
                        proxy_validated.add(hash)
                        print(f"Proxy validated: {hash}, {lib}")
                for lib in tor_services:
                    if lib in line:
                        tor_validated.add(hash)

                if "libtun2socks.so" in line:
                    libtun2sock_count += 1

        if not os.path.exists(os.path.join(data_dir, "ps_subprocess", f"{hash}.csv")):
            print(f"Could not find ps subprocess file for {hash}")
            continue

        with open(os.path.join(data_dir, "ps_subprocess", f"{hash}.csv"), "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.lower()
                if vpn_ps_check in line:
                    vpn_validated.add(hash)
                for lib in tor_services:
                    if lib in line:
                        tor_validated.add(hash)
                for lib in proxy_libraries:
                    if lib in line:
                        proxy_validated.add(hash)
                for lib in tor_bridge_libraries:
                    if lib in line:
                        tor_validated.add(hash)

                if "libtun2socks.so" in line:
                    pt_validated.add(hash)
                    libtun2sock_count += 1
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Error: {e}")

print(f"VPN validated: {len(vpn_validated)}")
print(f"Tor validated: {len(tor_validated)}")
print(f"Proxy validated: {len(proxy_validated)}")
print(f"PT validated: {len(pt_validated)}")
print(f"libtun2socks count: {libtun2sock_count}")

with open("vpn_validated.txt", "w") as f:
    f.write("\n".join(vpn_validated) + "\n")

with open("tor_validated.txt", "w") as f:
    f.write("\n".join(tor_validated) + "\n")

with open("proxy_validated.txt", "w") as f:
    f.write("\n".join(proxy_validated) + "\n")

with open("pt_validated.txt", "w") as f:
    f.write("\n".join(pt_validated) + "\n")