import os
import sys

for dirpath, dirnames, filenames in os.walk(sys.argv[1]):
    for filename in filenames:
        newname = (
            filename.replace("B0.1", "B00.10")
            .replace("B0.25", "B00.25")
            .replace("B0.5", "B00.50")
            .replace("B1.0", "B01.00")
            .replace("B2.0", "B02.00")
            .replace("B4.0", "B04.00")
            .replace("B10.0", "B10.00")
            .replace("b.1", "B00.10")
            .replace("b.25", "B00.25")
            .replace("b.5", "B00.50")
            .replace("b10", "B10.00")
            .replace("b1", "B01.00")
            .replace("b2", "B02.00")
            .replace("b4", "B04.00")
        )
        if filename != newname:
            print(f"{filename} -> {newname}")
        os.rename(os.path.join(dirpath, filename), os.path.join(dirpath, newname))
