# removes the carriage returns

import csv

# load the data
with open("case1-input.txt") as input, open("build/case1-input-normal.txt", "w") as output:
    reader = csv.reader(input, delimiter = "\t")

    for line in reader:
        output.write("\t".join(line) + "\n")
