import numpy as np
import argparse

VLOG_DATA_STR = "%(idx)s: data = %(wi)s\'b%(data)s;\n"


def vlog_rom(fname, data, word_wi):
    with open(fname, "w") as FH:
        for i, d in enumerate(data):
            FH.write(VLOG_DATA_STR % ({"idx": i, "wi": word_wi, "data": d}))
        FH.write(VLOG_DATA_STR % ({"idx": "default", "wi": word_wi, "data": str(0)}))
    print("Wrote %s" % fname)

def write_module(tag):
    basename = "lo_lut.v"
    fname = "lo_lut_%s.v" % tag
    vh_re = {"lo_lut" : "lo_lut_%s",
             "sin_lut.vh" : "sin_lut_%s.vh",
             "cos_lut.vh" : "cos_lut_%s.vh"}

    with open(basename, "r") as FH:
        lines = FH.readlines()
    with open(fname, "w") as FW:
        for l in lines:
            for k,v in vh_re.items():
                l = l.replace(k, v % tag)
            FW.write(l)

    print("Wrote %s" % fname)


def lo_gen(amp=1.0, ph_step="14/33", st_ph=0.0, rot="1/1", n_bits=18):
    ph_step = ph_step.split('/')
    frac_per = int(ph_step[0])
    full_per = int(ph_step[1])

    rot = rot.split('/')
    rot_ph = float(rot[0])/float(rot[1])

    rot_phasor = np.exp(1j*rot_ph*2*np.pi)

    sin_lut = []
    cos_lut = []
    for i in range(full_per):
        i = float(i + st_ph)

        sin_x = amp*np.sin(2*np.pi*(float(frac_per)/float(full_per))*i)
        cos_x = amp*np.cos(2*np.pi*(float(frac_per)/float(full_per))*i)

        cpx_rot = (rot_phasor)*(cos_x + 1j*sin_x)

        sin_x = np.imag(cpx_rot)
        cos_x = np.real(cpx_rot)

        # To signed binary
        sin_x = np.binary_repr(int(sin_x), width=n_bits)
        cos_x = np.binary_repr(int(cos_x), width=n_bits)

        sin_lut.append(sin_x)
        cos_lut.append(cos_x)

    return sin_lut, cos_lut


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a sin/cos look-up-table (LUT)')
    parser.add_argument('-a', '--amp', type=float, default=131071.1, #  2**17-1
                        help='LO amplitude')
    parser.add_argument('-p', '--ph_step', type=str, default="14/33",
                        help='Phase step as irreducible fraction')
    parser.add_argument('-b', '--bits', type=int, default=18,
                        help='LO word bit width')
    parser.add_argument('-s', '--start_ph', type=float, default=0.0,
                        help='Starting phase in fractions of phase step')
    parser.add_argument('-r', '--rot', type=str, default="1/1",
                        help='Supplemental phase shift as irreducible fraction')
    parser.add_argument('-t', '--tag', type=str, default='000',
                        help='LUT ID')
    args = parser.parse_args()

    sin_lut, cos_lut = lo_gen(args.amp, args.ph_step, args.start_ph, args.rot, args.bits)

    vlog_rom("sin_lut_%s.vh" % args.tag, sin_lut, args.bits)
    vlog_rom("cos_lut_%s.vh" % args.tag, cos_lut, args.bits)

    write_module(args.tag)

