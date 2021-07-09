# removes the carriage returns

import csv

rawfile = "case1-medB.txt"
newfile = "../psc/input/bgk-input-1-medB.txt"

# load the data
with open(rawfile) as input, open(newfile, "w") as output:
    reader = csv.reader(input, delimiter = "\t")

    for line in reader:
        output.write("\t".join(line) + "\n")
