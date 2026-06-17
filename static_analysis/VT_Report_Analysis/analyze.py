'''
This script is used to clean the json files obtained from VT and prepare them for avclass. It also creates a csv file with the hash, category, family, month, year and score of each file.
The process is as follows:
1. For each json file in the specified directory:
    a. Read the json file and extract the sha256 hash and the malicious score
    b. Write the json file in a single line format to a new directory
'''

import os
import json
import csv

cur_dir = "" # change this to the directory where the json files are located
out_dir = "" # change this to the directory where the cleaned files will be saved

year = 0 # change this to the year you want to process

with open("categories.json", "r") as f:
    categories = json.load(f)

csvfile = open(f"{year}.csv", "w")
csvwriter = csv.writer(csvfile)
csvwriter.writerow(["hash", "category", "family", "month", "year", "score"])

for dir in os.listdir(cur_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    scores = {}

    for i in os.listdir(f"{cur_dir}/{dir}"):
        try:
            with open(f"{cur_dir}/{dir}/{i}", "r") as f:
                lines = f.readlines()
                s = ""
                f.seek(0)
                data = json.load(f)
                scores[data["data"]["attributes"]["sha256"]] = data["data"]["attributes"]["last_analysis_stats"]["malicious"]
                with open(f"{out_dir}/{i}", "w") as out:
                    for i in lines:
                        s += i.strip()
                    out.write(s)
        except:
            continue

    os.system(f"avclass -d {out_dir} -hash sha256 -o output.txt")

    os.system(f"rm -r {out_dir}")

    with open("output.txt", "r") as f:
        lines = f.readlines()
        for i in lines:
            i = i.strip().split("\t")
            hash = i[0]
            family = i[1]
            if family == "-":
                continue
            category = ""
            if family.startswith("SINGLETON"):
                family = "SINGLETON"
            if family in categories:
                category = categories[family]

            csvwriter.writerow([hash, category, family, dir, year, scores[hash]])

csvfile.close()
