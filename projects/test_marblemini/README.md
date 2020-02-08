# Marble1

Initial programming support for [Marble Mini hardware](https://github.com/BerkeleyLab/Marble-Mini).
The Marble.xdc file here is the one generated by a script in that repository.

Infrastructure provided by [Bedrock](https://github.com/BerkeleyLab/Bedrock).

Currently tested successful at booting a bitfile (using [openocd](http://openocd.org/)),
bringing up Ethernet (default 192.168.19.8), blinking LEDs,
and reading/writing/booting SPI Flash (using Bedrock's spi_test.py).
There's a trivial utility (mutil) that documents common operations,
and [instructions](bringup.txt) for initial FPGA/Flash programming.
Also see the [todo list](todo).

Top-level needs more automated regression testing.  Concept for testing in simulation:

    make net_slave_run &
    python testcase.py --sim --ramtest --stop
    make lb_marble_slave_view

Hardware tests of the I2C subsystem (bedrock's i2cbridge gateware)
will configure and read out SFPs, read the write-protect status, FMC voltage and current, and blink LEDs:

    ./mutil usb
    python testcase.py --sfp --vcd=capture.vcd
    gtkwave capture.vcd
    python testcase.py --sfp --poll --rlen=64

Periodic output from that last step is something like:

    Write Protect switch is Off
    FMC1:  current  0.000 A   voltage  10.399 V
    FMC2:  current  0.119 A   voltage  10.399 V
    SFP1:  0xF
    SFP2:  0xB
      Temp     35.0 C
      Vcc      3.248 V
      Tx bias  0.0000 mA
      Tx pwr   0.0001 mW
      Rx pwr   0.0001 mW
    SFP3:  0xF
    SFP4:  0xF