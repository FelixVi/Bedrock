'''
Top-level multichannel plotter.
To be revamped with something more portable and GUI like (Kivy?)
For now, plots the number of channels selected using the banyan mask on the
input in an ultra hacky way, but as fast as it can get for Matplotlib
'''
import sys

import numpy as np
from scipy import signal as signal
from matplotlib import pyplot as plt
import matplotlib.animation as animation

from banyan_ch_find import banyan_ch_find
from banyan_spurs import collect_adcs
from prc import c_prc

FOO1, FOO2 = None, None
g_data = []

def write_mask(prc, mask_int):
    prc.reg_write([{'banyan_mask': mask_int}])
    channels = banyan_ch_find(mask_int)
    n_channels = len(channels)
    print((channels, 8 / n_channels))
    return n_channels, channels


def get_npt(prc):
    banyan_status = prc.reg_read_value(['banyan_status'])[0]
    npt = 1 << ((banyan_status >> 24) & 0x3F)
    if npt == 1:
        print("aborting since hardware module not present")
        sys.exit(2)
    return npt


class ADC:
    bits = 16
    scale = 1 << (bits - 1)  # signed
    sample_rate = 100000000.
    count_to_1volt = 1. / scale
    # 6dbm = 10 * log10(P/1e-3W)
    # 10 ** (6 / 10) = P / 1e-3
    # 10 ** (0.6) * 1e-3 = P
    # Assuming P = V**2 / 50 Ohms
    # V**2 = 1e-3 * (10 ** 0.6) * 50
    # V = np.sqrt(1e-3 * (10 ** 0.6) * 50)
    dbm_to_Vrms = np.sqrt(1e-3 * (10 ** 0.6) * 50)
    Vzp = dbm_to_Vrms * np.sqrt(2)


def counts_to_volts(raw_counts):
    # TODO: This should be adjusted to ADC.Vzp and verified
    return raw_counts * ADC.count_to_1volt


def run(ip_addr='192.168.1.121',
        port=50006,
        mask="0xff",
        npt_wish=0,
        count=10,
        verbose=False,
        filewritepath=None,
        use_spartan=False):

    mask_int = int(mask, 0)
    prc = c_prc(
        ip_addr, port, filewritepath=filewritepath, use_spartan=use_spartan)

    npt = get_npt(prc)
    n_channels, channels = write_mask(prc, mask_int)
    pts_per_ch = npt * 8 // n_channels
    print('Points per ch: {}'.format(pts_per_ch))

    fig, axes = plt.subplots(nrows=n_channels)
    # axes = [axes] if n_channels == 1 else axes
    styles = ['r-', 'g-', 'y-', 'm-'][:n_channels]

    x = np.arange(0, pts_per_ch) / 10e9
    x = np.fft.rfftfreq(pts_per_ch, d=1 / ADC.sample_rate)
    y = np.sin(x)

    def plot(ax, style, ch):
        line = ax.plot(x, y, style, label=ch, animated=True)[0]
        ax.set_ylabel('ADC data scaled to +/-1v')
        ax.set_xlabel('Freq[Hz]')
        ax.legend()
        ax.set_xscale('log')
        ax.set_yscale('log')
        return line

    lines = [plot(ax, style, ch) for ax, style, ch in zip(axes, styles, channels)]

    def csd_plot(ax, style, ch):
        line = ax.plot(x, y/1e7, style, label=ch, animated=True)[0]
        ax.set_ylabel('ADC data scaled to +/-1v')
        ax.set_xlabel('Time[us]')
        ax.legend()
        ax.set_yscale('log')
        return line

    fig2, axes2 = plt.subplots(1)
    csd_lines = [csd_plot(axes2, styles[-1], 'csd')]

    def animate(x):
        global g_data
        # collect_adcs is not normal:
        # It always collects npt * 8 data points.
        # Each channel gets [(npt * 8) // n_channels] datapoints
        (data_block, timestamp) = collect_adcs(prc, npt, n_channels)
        nblock = counts_to_volts(np.array(data_block)) # ADC count / FULL SCALE => [-1.0, 1.0]
        for j, line in enumerate(lines, start=1):
            ax = axes[j - 1]
            ax.relim()
            ax.autoscale_view()
            ch_data = nblock[j - 1]
            # rfft = np.abs(np.fft.rfft(ch_data))
            f, psd = signal.periodogram(ch_data, ADC.sample_rate, 'hanning')
            line.set_ydata(np.sqrt(np.abs(psd)))
            line.set_xdata(f)
        # do cross power
        g_data = signal.csd(nblock[0], nblock[1], ADC.sample_rate)
        return lines

    def animate2(x):
        global g_data
        if g_data:
            f, Pxy = g_data
            csd_lines[0].set_xdata(f)
            csd_lines[0].set_ydata(np.sqrt(np.abs(Pxy)))
        return csd_lines

    # npt_wish only works correctly if mask is 0xff
    # This kind of sort of makes sense, but can be elided to the normal user
    if npt_wish and npt_wish < npt and mask_int == 0xff:
        npt = npt_wish
    print(("npt = {}".format(npt)))

    # We'd normally specify a reasonable "interval" here...
    global FOO, FOO1, FOO2
    FOO1 = animation.FuncAnimation(fig, animate, interval=0.1, blit=True)
    FOO2 = animation.FuncAnimation(fig2, animate2, interval=0.1, blit=True)
    plt.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Read/Write from FPGA memory')
    parser.add_argument(
        '-a',
        '--ip',
        help='ip_address',
        dest='ip',
        type=str,
        default='192.168.1.121')
    parser.add_argument(
        '-p', '--port', help='port', dest='port', type=int, default=50006)
    parser.add_argument(
        '-m', '--mask', help='mask', dest='mask', type=str, default='0x3')
    parser.add_argument(
        '-n',
        '--npt_wish',
        help='number of points per channel',
        type=int,
        default=4096)
    parser.add_argument(
        '-c', '--count', help='number of acquisitions', type=int, default=1)
    parser.add_argument(
        '-f', '--filewritepath', help='static file out', type=str, default="")
    parser.add_argument(
        "-u",
        "--use_spartan",
        action="store_true",
        help="use spartan",
        default=True)
    args = parser.parse_args()
    run(ip_addr=args.ip,
        port=args.port,
        mask=args.mask,
        npt_wish=args.npt_wish,
        count=args.count,
        filewritepath=args.filewritepath,
        use_spartan=args.use_spartan)
