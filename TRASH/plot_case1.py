import numpy as np
import matplotlib.pyplot as plt
# from matplotlib import cm
import csv
import sys

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <col>")
    quit()

# Which columns to plot.
# The columns: 0=rho, 1=ne, 2=v_phi, 3=Te, 4=E_rho
# Rho is always the independent variable.
cols = [0] + [int(arg) for arg in sys.argv[1:]]
col_names = {0:"rho", 1:"ne", 2:"v_phi", 3:"Te", 4:"E_rho"}
num_rows = 4401

data = np.zeros([num_rows, len(cols)])


# load the data
with open("case1-input.txt") as tsv:
    reader = csv.reader(tsv, delimiter = "\t")

    # skip first line
    next(reader)
    i = 0
    for line in reader:
        data[i,:] = [float(line[col]) for col in cols]
        i += 1


plt.plot(data[:,0], data[:,1])
plt.title(col_names[cols[1]])
plt.xlabel(col_names[0])
plt.ylabel(col_names[cols[1]])
plt.show()