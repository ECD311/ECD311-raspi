import sys
import os
import glob
import pandas as pd

src = "archive/"

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


for file in os.listdir(src):
    if os.path.isdir(src+file):
        year = file.split("/")[-1]
        for month in range(1,13):
            for day in range(1,32):
                files = os.path.join(src, file, str(month), "data_log_*_*_%02i_*.csv" % day)
                files = glob.glob(files)
                try:
                    combined_csv = pd.concat([pd.read_csv(f) for f in files])
                except:
                    continue
                combined_csv.to_csv(os.path.join(src, str(year), str(month), "data_log_%s_%s_%s.csv" % (year, month, day)))
                print(os.path.join(src, str(year), str(month), "data_log_%s_%s_%s.csv" % (year, month, day)))

# remove existing files after concat
