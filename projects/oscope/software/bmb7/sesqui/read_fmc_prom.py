#!/bin/env python

import qf2_pre_spartan as board
import argparse

parser = argparse.ArgumentParser(description='Display QF2-pre FMC PROM data', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
args = parser.parse_args()

# Start the class
x = board.interface(args.target)

# Most PROMs have similar basic behavior on the QF2-pre, but the exact addressing varies.
# Typically, the PROM base address is (0x50 | ADDR), where ADDR == 0 to 7 depending on how GA0 & GA1 are wired up.
# In the QF2-pre, the top FMC is GA0 = GA1 = 0, the bottom FMC is GA0 = 1, GA1 = 0.

# For the HW-FMC-105-DEBUG: TOP FMC == 0x50, BOTTOM FMC == 0x52, DEVICE == m24c02
# For the LCLS-II ADC mezzanine: TOP FMC == 0x50, BOTTOM FMC == 0x51, DEVICE == at24c32d

# To read or write a byte from a given address, use:
# write_[DEVICE]_prom(PROM ADDRESS, ADDRESS, BYTE)
# read_[DEVICE]_prom(PROM ADDRESS, ADDRESS, BYTE)

################################
# Example: Read first 10 bytes from M24C02 PROM on HW-FMC-105-DEBUG mounted on top FMC site
# Modified to read first 27 bytes from AT24C32D PROM on LBNL Digitizer board

bottom_site = False
PROM_ADDRESS = 0x52 if bottom_site else 0x50

#for i in range(0, 10):
#   x.write_m24c02_prom(PROM_ADDRESS, i, i)

for i in range(0, 27):
    # pv = x.read_m24c02_prom(PROM_ADDRESS, i, bottom_site)
    pv = x.read_at24c32d_prom(PROM_ADDRESS, i, bottom_site)
    suff = "\t"+chr(pv) if 32 <= pv < 127 else ""
    print str(i)+'\t'+str(hex(pv))+suff

################################
# Example: Read first 10 bytes from AT24C32D PROM on LCLS-II ADC mezzanine mounted on top FMC site

#PROM_ADDRESS = 0x50 # 0x51 for bottom FMC site

#for i in range(0, 10):
#   x.write_at24c32d_prom(PROM_ADDRESS, i, i)

#for i in range(0, 10):
#   print str(i)+'\t'+str(hex(x.read_at24c32d_prom(PROM_ADDRESS, i)))
