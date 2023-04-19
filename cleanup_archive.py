import sys
import os
import glob
import pandas as pd

src = "archive/"
to_delete = []

for file in glob.glob(src+"*.csv"):
    print(file)
    try:
        year = file.split("_")[2]
    except:
        continue
    try:
        month = file.split("_")[3]
    except:
        continue
    if not os.path.exists(src + year):
        os.mkdir(src + year)
    if not os.path.exists(src + year + "/" + month):
        os.mkdir(src + year + "/" + month)
    os.rename(file, src + year+ "/" + month + "/" + file.split("/")[-1])
    to_delete.append(src + year+ "/" + month + "/" + file.split("/")[-1])


for file in os.listdir(src):
    if os.path.isdir(src+file):
        year = file.split("/")[-1]
        print(year)
        for month in range(1,13):
            for day in range(1,32):
                files = os.path.join(src, file, "%02i" % month, "data_log_%s_%02i_%02i_*.csv" % (year, month, day))
                files = glob.glob(files)
                try:
                    combined_csv = pd.concat([pd.read_csv(f) for f in files])
                except:
                    continue
                combined_csv.to_csv(os.path.join(src, str(year), "%02i" % month, "data_log_%s_%02i_%02i.csv" % (year, month, day)), index=False)
                print(os.path.join(src, str(year), "%02i" % month, "data_log_%s_%02i_%02i.csv" % (year, month, day)))

# remove existing files after concat

for file in to_delete:
    os.remove(file)