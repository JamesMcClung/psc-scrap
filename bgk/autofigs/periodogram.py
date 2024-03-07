import scipy.signal as sig

from . import util
from bgk.field_data import FieldData
from .image import ImageParams, image_generator

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes


__all__ = ["plot_periodogram"]


@image_generator("periodogram")
def plot_periodogram(image_params: ImageParams, fig: Figure = None, ax: Axes = None, annotate: bool = True) -> tuple[Figure, Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    data = image_params.fields.get_means_at_origin()
    idx_freq, power = sig.periodogram(data, nfft=len(data) * 4)
    freq = idx_freq * len(image_params.fields.axis_t) / image_params.fields.axis_t.values[-1]

    if annotate:
        for peak_idx in sig.find_peaks(power, prominence=power.max() / 10)[0]:
            peak_freq = freq[peak_idx]
            peak_power = power[peak_idx]
            ax.annotate(f"{peak_freq:.3f}", xy=(peak_freq, peak_power))

    ax.set_xlabel("Frequency")
    ax.set_ylabel("Amplitude")
    ax.set_title(f"Periodogram of $n_e(0,0)$ ($B_0={image_params.fields.params_record.B0}$, {image_params.fields.case_name})")

    ax.plot(freq, power)
    return fig, ax
