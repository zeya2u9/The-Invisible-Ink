import os
import csv

output_file = "running_apps.csv"
output = open(output_file, "w")
writer = csv.writer(output)

input_file = "input.csv"
input = open(input_file, "r")
reader = csv.reader(input)

current_hashes = [i.lower().split(".")[0] for i in os.listdir("/apks")]
writer.writerow(next(reader))

for row in reader:
    if row[0].lower() in current_hashes:
        writer.writerow(row)