# import h5py
# import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

from .output_reader import readParam, Loader
from .input_reader import Input

##########################


def read_step(step: int, electronsOnly: bool = True):
    rank = 0
    df = pd.read_hdf(path + f"prt.{step:06d}_p{rank:06d}.h5", "particles/p0/1d")
    df.drop(columns=["x", "px", "m", "w", "tag"], inplace=True)
    if electronsOnly:
        df = df[df.q == -1]
        df.drop(columns=["q"], inplace=True)
    df["step"] = step
    return df


def plot_distribution(df, x: str, y: str):
    fig, ax = plt.subplots(1, 1)
    df.plot.hexbin(x, y, gridsize=50, ax=ax)
    ax.set_title(f"f({x}, {y}) at t={t} for B={B}")
    if x.endswith(tuple("y, z")) and y.endswith(tuple("y, z")):
        ax.set_aspect(1.0)


##########################

path = "/mnt/lustre/IAM851/jm1667/psc-runs/case1/single_truedist/B1/"

inputFile = readParam(path, "path_to_data", str)
B = readParam(path, "H_x", float)
maxStep = readParam(path, "nmax", int)
ve_coef = readParam(path, "v_e_coef", float)

print(f"path={path}")
print(f"input={inputFile}")
print(f"max step={maxStep}")
print(f"B={B}")
print(f"ve_coef={ve_coef}")

##########################

step = 0
t: float = Loader(path, engine="pscadios2", species_names=["e", "i"])._get_xr_dataset("pfd", step).time
print(f"t={t}")

df = read_step(step)
input = Input(inputFile)

df["r"] = (df.y**2 + df.z**2) ** 0.5
df["v_phi"] = (df.pz * df.y - df.py * df.z) / df.r
df["v_rho"] = (df.py * df.y + df.pz * df.z) / df.r
df.v_rho.fillna(0, inplace=True)
df.v_phi.fillna(0, inplace=True)
# df["w"] = (df.py ** 2 + df.pz ** 2) / 2 - df.r.map(lambda r: input.interpolate_value(r, "Psi"))
# df["l"] = 2 * df.r * df.v_phi - B * df.r ** 2

##########################

hist, rhos, v_phis = np.histogram2d(df.r, df.v_phi, bins=[60, 80])

v_phis_cc = (v_phis[1:] + v_phis[:-1]) / 2
rhos_cc = (rhos[1:] + rhos[:-1]) / 2
fs2d = hist.T / rhos_cc

mean_v_phis = fs2d.T.dot(v_phis_cc) / fs2d.sum(axis=0)
mean_v_phis_input = np.array([input.interpolate_value(rho, "v_phi") for rho in rhos_cc])

##########################

plt.pcolormesh(rhos, v_phis, fs2d, cmap="Reds")
plt.xlabel("$\\rho$")
plt.ylabel("$v_\\phi$")
plt.plot(rhos_cc, mean_v_phis, "k", label="actual mean")
plt.plot(rhos_cc, mean_v_phis_input, "b", label="target mean")
plt.title(f"f($\\rho$, $v_\\phi$) at t={t:.3f} for $B={B}$")
plt.colorbar()
plt.legend()
plt.ylim(-0.003, 0.003)
plt.show()
