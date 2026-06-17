import os
from hashlib import sha256
from androguard.core.bytecodes import apk as APK
import logging
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import pickle
from androguard.core.bytecodes import dvm
import os

done = set()

output_writer_lock = threading.Lock()


i2p_routerconfig_strings = [ 
 "i2np.ntcp.enable",
 "i2np.udp.enable", 
 "i2np.ntcp2.enable",
 "router.inboundPool",
 "router.outboundPool"
]

tor_bridge_libraries = set([
    "libtun2socks.so",
    "libsnowflake.so",
    "libobfs4proxy.so",
    "libwebtunnel.so",
    "libconjure.so"
])

tor_service_list = set()

with open("proxy_packages.txt", "r") as f:
    lines = f.readlines()

libraries = [line.strip().split(',')[0] for line in lines]

with open("tor_services.txt") as f:
    for i in f.readlines():
        tor_service_list.add(i.strip())

tor_bridge_list = set()

with open("tor_bridge_services.txt") as f:
    for i in f.readlines():
        tor_bridge_list.add(i.strip())

logger = logging.getLogger(__name__)
logging.basicConfig(filename='info.log', filemode="a", level=logging.DEBUG)

class StaticAnalyzer:
    def load_apk(apk_path):
        return APK.APK(apk_path)

    def check_tor(apk):
        for file_name in apk.get_files():
            if os.path.basename(file_name).lower() in ["tor", "torrc"]:
                return file_name
            if os.path.basename(file_name).lower() in ["tor.so", "libtor.so"]:
                return file_name
            
        return None
    
    def check_i2p(apk, apk_name):

        for file_name in apk.get_files():
            if os.path.basename(file_name).lower() in ["i2ptunnel_config", "help_i2ptunnel.html", "i2pd.conf", "i2pcrt.crt"]:
                return file_name
            if os.path.basename(file_name).lower() in ["libjbigi.so", "libi2p.so", "libi2pd.so", "libinvizible.so"]:
                return file_name
            
            # Checking the contents of the router_config file. 
            if os.path.basename(file_name).lower() in ["router_config", "logger_config"]:
                print(f"Found routers_config: {file_name}")

                content = apk.get_file(file_name).decode(errors="ignore")

                if os.path.basename(file_name).lower() == "router_config":
                    for s in i2p_routerconfig_strings:
                        if s in content:
                            return file_name
                    

                elif os.path.basename(file_name).lower() == "logger_config":
                    identifier_string = "logger.record.net.i2p"

                    if identifier_string in content:
                        return file_name

        all_classes = StaticAnalyzer.get_all_classes(apk_name, apk)

        all_packages = StaticAnalyzer.get_package_names(all_classes)

        # print(all_packages)

        for package in all_packages:
            if package.startswith('net.i2p'):
                return package

        return None
    
    def check_freenet(apk):
        for file_name in apk.get_files():
            if os.path.basename(file_name).lower().endswith(".fref"):
                logger.info(f"File ends with fref {file_name}")
                expected_keys = [
                    "identity=", "location=", "opennet=", "sigP256=", "physical.udp=", "End"
                ]
                try:
                    content = apk.get_file(file_name).decode(errors="ignore")  # Read file content
                    lines = content.strip().split("\n")
                    
                    missing_keys = [key for key in expected_keys if not any(line.startswith(key) for line in lines)]
                    
                    if missing_keys:
                        logger.info(f"Missing keys in {file_name}: {missing_keys}")
                    else:
                        logger.info(f"Valid .fref file: {file_name}")
                        return file_name

                except Exception as e:
                    logger.info(f"Error reading file: {e}")

            if os.path.basename(file_name).lower().endswith(".ini"):
                print(f"File ends with ini {file_name}")
                expected_keys = [
                    "console.enabled", "fproxy.enabled", "fproxy.port", "fproxy.bindTo", "node.listenPort", "node.storeSize",
                    "node.storeType", "node.bindTo", "node.opennet.enabled", "node.opennet.listenPort", "node.opennet.bindTo"
                ]
                try:
                    content = apk.get_file(file_name).decode(errors="ignore")  # Read file content
                    lines = content.strip().split("\n")
                    
                    missing_keys = [key for key in expected_keys if not any(line.startswith(key) for line in lines)]
                    
                    if missing_keys:
                        logger.info(f"Missing keys in {file_name}: {missing_keys}")
                    else:
                        logger.info(f"Valid .fref file: {file_name}")
                        return file_name

                except Exception as e:
                    logger.info(f"Error reading file: {e}")

        return None
    
    def get_all_classes(apk_name, apk):
        classes = set()

        logger.debug(f"Processing APK: {apk_name}")
        print(f"Processing APK: {apk_name}")

        for dex in apk.get_all_dex():
            try:
                dex = dvm.DalvikVMFormat(dex)
            except Exception as e:
                logger.error(f"Error processing DEX in {apk_name}: {str(e)}")
                continue

            # Collect and normalize all class names
            for clazz in dex.get_classes():
                # Normalize the class name (remove 'L' and ';', replace '/' with '.')
                clazz_name = str(clazz.get_name()).replace("/", ".")[1:-1]
                logger.debug(f"Found class: {clazz_name}")
                classes.add(clazz_name)

        return classes

    def get_package_names(all_classes):
        packages = set()
        for clazz in all_classes:
            # Extract the package name from the class name (remove the class itself)
            package_name = ".".join(clazz.split(".")[:-1])
            packages.add(package_name)

        return packages

    def check_proxy(apk, apk_name):
        main_package_name = apk.get_package()
        logger.info(f"Main package name: {main_package_name}")

        all_classes = StaticAnalyzer.get_all_classes(apk_name, apk)

        all_packages = StaticAnalyzer.get_package_names(all_classes)

        for library in libraries:
            if library in all_packages:
                return library
            
        return None
    
    def check_vpn(apk):
        for service in apk.get_services():
            intent_filters = apk.get_intent_filters("service", service)
            if "action" in intent_filters:
                if "android.net.VpnService" in intent_filters["action"] and service not in tor_service_list and service not in tor_bridge_list:
                    return service
                
        return None
    
    def check_tor_bridge(apk):
        for file_name in apk.get_files():
            for lib in tor_bridge_libraries:
                if lib == os.path.basename(file_name.lower()):
                    return lib

        for service in apk.get_services():
            if service in tor_bridge_list:
                return service
            
        return None
    
    def process_apk(apk_path, hash):
        if hash in done:
            logger.info(f"Skipping {apk_path} as it has already been processed")
            return
        else:
            done.add(hash)
        
        local_apk_path = apk_path
        
        try:
            with open(local_apk_path, "rb") as f:
                data = f.read()
                hash_computed = sha256(data).hexdigest()

            if hash.strip().lower() != hash_computed.strip().lower():
                logger.info(f"Hash mismatch for {apk_path}")

            apk = StaticAnalyzer.load_apk(local_apk_path)
            tor = StaticAnalyzer.check_tor(apk)
            vpn = StaticAnalyzer.check_vpn(apk)
            proxy = StaticAnalyzer.check_proxy(apk, hash)
            tor_bridge = StaticAnalyzer.check_tor_bridge(apk)
            freenet = StaticAnalyzer.check_freenet(apk)
            i2p = StaticAnalyzer.check_i2p(apk, hash)
            
            if(not tor and not vpn and not tor_bridge and not proxy and not freenet and not i2p):
                logger.info(f"Deleting file {apk_path}")
                os.remove(local_apk_path)

            if not tor:
                tor = ""

            if not vpn:
                vpn = ""

            if not tor_bridge:
                tor_bridge = ""
            
            if not proxy:
                proxy = ""
            
            if not i2p:
                i2p = ""

            if not freenet:
                freenet = ""

            return hash, apk.get_package(), tor, tor_bridge, vpn, proxy, i2p, freenet, apk_path
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print(f"Error processing {apk_path}: {e}")
            os.remove(local_apk_path)
            logger.error(f"Error processing {apk_path}: {e}")
                            

def main(apk_path, hash):
    return StaticAnalyzer.process_apk(apk_path, hash)