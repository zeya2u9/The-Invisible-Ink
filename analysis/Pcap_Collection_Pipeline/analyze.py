'''
This module analyzes APK files to extract the package name and main activity using Androguard.
It reads APK paths from 'apk_paths.txt', performs analysis, and saves results to 'apk
'''

from androguard.misc import AnalyzeAPK

def analyze_apk(path):
    try:
        a, _, _ = AnalyzeAPK(path)
        package_name = a.get_package()
        main_activity = a.get_main_activity()
        return package_name, main_activity
    except Exception as e:
        print(f"Error analyzing APK: {e}")
        return None, None


def run():
    with open("apk_paths.txt") as f:
        hashes = f.readlines()

    paths = ["/" + hash.strip() + ".apk" for hash in hashes]

    with open("apk_analysis_results.txt", "w") as output_file, open("failed_analysis.txt", "w") as failed_file:
        for i in range (0, len(paths)):
            path = paths[i]
            hash = hashes[i]
            print(f"Analyzing {path}...")
            path = path.strip()

            package_name, main_activity = analyze_apk(path)
            
            if package_name is None or main_activity is None:
                failed_file.write("{}\n".format(path))
                continue
            else:
                output_file.write("{}\t".format(path))
                output_file.write("{}\t".format(package_name))
                output_file.write("{}\t".format(main_activity))
                output_file.write("{}".format(hash))

    return "apk_analysis_results.txt"
