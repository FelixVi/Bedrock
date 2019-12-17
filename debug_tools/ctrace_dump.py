from datetime import datetime


def tobin(x, count=8):
    # Integer to binary; count is number of bits
    # Some credit to W.J. van der Laan in
    # http://code.activestate.com/recipes/219300/
    return [(x >> y) & 1 for y in range(count-1, -1, -1)]


def vcd_header(fh, sigs, first, timescale="1ns", now=None):
    dw = len(sigs)
    if not now:
        now = datetime.isoformat(datetime.utcnow())
    print("$date %s $end" % now, file=fh)
    print("$version c2vcd $end", file=fh)
    print("$timescale %s $end" % timescale, file=fh)
    print("$scope module logic $end", file=fh)
    for ix in range(dw):
        print("$var wire 1 %s %s $end" % (chr(65+ix), sigs[ix]), file=fh)
    print("$upscope $end", file=fh)
    print("$enddefinitions $end", file=fh)
    print("$dumpvars", file=fh)
    for ix in range(dw):
        print("b%d %s" % (first[ix], chr(65+ix)), file=fh)
    print("$end", file=fh)


# 50 MHz and ns time step means multiply integer time count by 20
# tw parameter should be configured to match that set for ctrace.v
def write_vcd(fh, sigs, data, tstep=20, tw=16):
    dw = len(sigs)  # this also needs to match ctrace.v parameter
    t = 0
    pc = 0
    mtime = 1 << tw
    data_mask = (1 << dw) - 1
    old_vbin = None
    for a in data:
        dt = a >> dw
        if dt == 0:
            dt = mtime
        t = t + dt
        v = a & data_mask
        vbin = tobin(v, count=dw)
        if pc == 0:
            vcd_header(fh, sigs, vbin)
        else:
            for ix in range(dw):
                if vbin[ix] != old_vbin[ix]:
                    print("b%d %s" % (vbin[ix], chr(65+ix)), file=fh)
        print("#%d" % (t*tstep), file=fh)
        old_vbin = vbin
        pc += 1


def usage():
    print('python ctrace_dump.py -i ctrace.dat -o foo.vcd')


if __name__ == "__main__":
    import sys
    import getopt
    larglist = 'help', 'i=', 'o='
    opts, args = getopt.getopt(sys.argv[1:], 'hi:o:', larglist)
    do_start = False
    do_dump = False
    out_file = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-i', '--input'):
            in_file = arg
        elif opt in ('-o', '--output'):
            out_file = arg

    # signals should be runtime config
    # this static configuration matches application_top.v
    signals = ["ack_match",
               "consistency_match",
               "abl_match",
               "link_timer_on",
               "lacr_in_stb"]

    signals = ["rx_valid"] + ["rx_data0%2.2d" % jx for jx in range(15-1, -1, -1)]
    print(signals)
    tw = 16
    aw = 16

    raw_dat = []
    hex_set = set('abcdefABCDEF')
    with open(in_file, 'r') as FH:
        line = FH.readlines()[0]
        for it in line.split():
            if any((c in hex_set) for c in it):
                raw_dat.append(int(it, 16))
            else:
                raw_dat.append(int(it))

    with open(out_file, 'w') as FH:
        write_vcd(FH, signals, raw_dat, tstep=8, tw=tw)