import csv
import os

csv_file = "final_dataset_static.csv"
csv_file = open(csv_file)
csv_reader = csv.DictReader(csv_file)

done_list = "done_list.txt"
done_list = open(done_list, "r")
done_list = done_list.readlines()
done_list ={x.strip().lower():line for line, x in enumerate(done_list) if x.strip()}

with open("done_list.txt") as f:
    for line, x in enumerate(f):
        x = x.strip()
        done_list[x] = line

pcap_list = os.listdir("pcaps")
pcap_list = set([x.split(".")[0].lower() for x in pcap_list])

out_file = "dynamic_dataset.csv"
out_file = open(out_file, "w")
out_file_writer = csv.writer(out_file)

header = False

for row in csv_reader:
    if not header:
        header = True
        out_file_writer.writerow(list(row.keys()) + ["dynamic", "pcap", "line"])
    if row["hash"].lower() not in done_list:
        continue

    row["dynamic"] = True
    row["pcap"] = row["hash"].lower() in pcap_list
    if row["hash"].lower() in done_list:
        row["line"] = done_list[row["hash"].lower()]

    out_file_writer.writerow(row.values())

out_file.close()
