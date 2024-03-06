import scipy.signal as sig

from . import util
from bgk.output_reader import FieldData

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes


__all__ = ["plot_periodogram"]


def plot_periodogram(videoMaker: FieldData, fig: Figure = None, ax: Axes = None, annotate: bool = True) -> tuple[Figure, Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    data = videoMaker.get_means_at_origin()
    idx_freq, power = sig.periodogram(data, nfft=len(data) * 4)
    freq = idx_freq * len(videoMaker.axis_t) / videoMaker.axis_t.values[-1]

    if annotate:
        for peak_idx in sig.find_peaks(power, prominence=power.max() / 10)[0]:
            peak_freq = freq[peak_idx]
            peak_power = power[peak_idx]
            ax.annotate(f"{peak_freq:.3f}", xy=(peak_freq, peak_power))

    ax.set_xlabel("Frequency")
    ax.set_ylabel("Amplitude")
    ax.set_title(f"Periodogram of $n_e(0,0)$ ($B_0={videoMaker.params_record.B0}$, {videoMaker.case_name})")

    ax.plot(freq, power)
    return fig, ax
