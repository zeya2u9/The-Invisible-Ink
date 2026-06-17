import csv

def get_hashes(csv_file_path, done=set()):
    hashes = []
    years = []
    months = []

    try:
        with open(csv_file_path, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["Hash"] in done:
                    continue
                hashes.append(row['Hash'])
                years.append(int(row['Year']))
                months.append(int(row['Month']))
    except Exception as e:
        print(f"An error occurred: {e}")
        return [], [], []

    return hashes, years, months
