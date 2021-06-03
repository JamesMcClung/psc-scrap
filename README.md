A mini-project for PSC. We have `case1-input.txt` and want to a) plot it and b) parse it in C++.

# Usage

## Plotting

Run `python3 plot.py col`, where `col` is the column (0-4) of the dependent variable to plot against `rho`. See `case1-input.txt` for the columns.

## Parsing

First make the `build` folder with CMake. Then run `python3 refactor.py` to convert `case1-input.txt` to `build/case1-input-normal.txt`, which is identical except uses no carriage returns. Then you can execute `build/parse`.