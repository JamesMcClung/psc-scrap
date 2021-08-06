# removes the carriage returns

import csv
import sys

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} bad/file/path cleaned/file/path")
    exit(1)

rawfile = sys.argv[1]
newfile = sys.argv[2]

# load the data
with open(rawfile) as input, open(newfile, "w") as output:
    reader = csv.reader(input, delimiter = "\t")

    for line in reader:
        output.write("\t".join(line) + "\n")
