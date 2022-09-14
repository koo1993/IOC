# import required module
import os
import json
import csv
import pandas as pd

# assign directory
directory = 'toprocess'

# iterate over files in
# that directory


header = ['ip', 'isp', 'watermark']
# now we will open a file for writing
data_file = open('result.csv', 'w')
csv_writer = csv.writer(data_file)
csv_writer.writerow(header)

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        print(f)
        f = open(f, 'r')
        data = json.load(f)
        f.close()
        for eachscan in data:
            row_data = []
            row_data.append(eachscan['ip'])
            try:
                row_data.append(eachscan['isp'])
            except:
                row_data.append(eachscan['isp_iplocation_net'])
                print("catched")
            row_data.append(eachscan['watermark'])
            csv_writer.writerow(row_data)
data_file.close()

file_name = "result.csv"
file_name_output = "result_without_dupes.csv"
df = pd.read_csv(file_name)

# Notes:
# - the `subset=None` means that every column is used
#    to determine if two rows are different; to change that specify
#    the columns as an array
# - the `inplace=True` means that the data structure is changed and
#   the duplicate rows are gone
df.drop_duplicates(subset=None, inplace=True)

# Write the results to a different file
df.to_csv(file_name_output, index=False)