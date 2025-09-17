# Two programs to create a bridge between a Windows desktop's USB serial COM port and a Linux server

## Warning!

Please read the security section. In summary everything sent across the
"bridge" in both directions is sent unencrypted.

USE AT YOUR OWN RISK!!!

## Abstract

The programs here were written to overcome an issue I was having trying
to get an Ubuntu 24.04 LTS virtual machine which runs under Virtual
Box on my Windows 10 (soon to be Windows 11) laptop to talk to a USB to
serial adapter.

When I connected a USB to serial adapter to one of the laptops USB
ports I could map the USB device ok and see it on the Ubuntu machine
as /dev/ttyUSB0 but trying to use it would initially work but then hang
and/or become otherwise unreliable.

Sometimes the Ubuntu virtual machine would not restart properly.

Some googling shows other people have had issues with USB to serial
adaptors and Virtual Box.

Rather than try the many workarounds suggested I have taken a different
approach.

I have written two programs that work as a bridge between the USB to
serial adapter in Windows and the Ubuntu virtual machine hosted by
Virtual Box.

Here is a diagram:

```
+---------------+
| Serial Device |
+---------------+
        |                         +-----------------------+
        `--- RJ45 to DB9 Cable ---| USB to serial Adapter |---
                                  +-----------------------+   \
                                                              |
     +--------------------------+                             |
     | LAPTOP                   |                             /
     |                          |-----------------------------
     | +----------------------+ |
     | | Virtual Box          | |
     | |                      | |
     | | +------------------+ | |
     | | | Ubuntu 24.04 LTS | | |
     | | | Virtual Machine  | | |
     | | +------------------+ | |
     | |                      | |
     | +----------------------+ |
     |                          |
     +--------------------------+
```

# Quick start

Copy the `tcb-server-w.py` Python 3 program to the Windows laptop.

Open a command prompt and change to the directory that `tcb-server-w.py` was copied to.

Run the program with:

```
python tcb-server-w.py --bind 10.7.0.10 --baud 9600
```

Change the IP address to the IP address of the laptop.

Copy the `Makefile` and `tcb-client-l.c` files to the Ubuntu 24.04 LTS virtual machine.

Login into the Ubuntu 24.04 LTS virtual machine.

Change to the directory that both files were copied to.

Run:

```
make
```

to compile the executable `$HOME/bin/tcb-client-l` - if the subdirectory `$HOME/bin` does
not exist then create it *BEFORE* running the `make` command.

Now run the `tcb-client-l` command as:

```
tcb-client-l 10.7.0.10
```

If connection is succesful the following will be displayed:

```
<<Connected>>
```

You will now be connected to the serial device at the end of the USB to serial adapter.

Try pressing return one or more times to get a login prompt or other output from the serial device.

To disconnect type the single character ^ and the following should be displayed:

```
<<Exiting>>
```

and the `tcb-client-l` program will terminate.

Both the `tcb-client-l` C program and the `tcb-server-w.py` Python program take
a range of optional command line arguments. See later sections in the README file
for details.

## Command line arguments for the tcb-server-w.py Python program

### The --com command line argument

The `--com` command line argument can be used to specify which COM port on the Windows
machine open.

If there is only one COM port available the `--com` command line argument is not necessary
as the program will determine the name of the single COM port.

If the `--com` command line argument is not specified are there are two or more COM ports
available on the Windows machine then the one with the highest number will be used. For example if the following
COM ports are available:

```
COM1   COM2   COM14
```

then COM14 will be used.

### The --baud command line argument

The baud rate to open the COM port at defaults to 9600 baud. To specify a different baud rate use
the `--baud` command lne argument. For example to use baud rate 115200 run the `tcb-server-w.py`
program as follows:

```
python tcb-server-w.py --baud 115200
```
### The --bind command line argument

The `--bind` command line agument is used to specify the IPv4 address that the `tcb-server-w.py`
program should listen on for incomining connections.

If `--bind` command line agument is omitted the `tcb-server-w.py` will see if there are any intefaces which have an IPv4 address where
the first two octets are 10 and 7 such as:

```
10.7.0.10
```

This is a hack to match my own test networks and save me, the program author, some typing :-]

### The --port command line argument

The `--port` command line argument is used to specifiy the TCP/IP port number the `tcb-server-w.py` should listen on.

It defaults to port 8089 but if a different port number is needed is can be specified. For example:

```
python tcb-server-w.py --port 9123
```

### The --timeout command line argument

The `--timeout` command line argument should never really be required but is included for experimentation and testing.

The value is a floating point number which defaults to 0.01 seconds. This is the time to wait for input to arrive on both
the COM port and the TCP/IP port. Smaller values will make the program more responsive at the expense of extra CPU cycles. Larger numbers
will make the program "laggy" to the point of unusability.

Depending on your hardware sepcpfications you might want to try different values but 0.01 seconds (i.e. one hundredth of a second)
has, so far, been satisfactory.


## Command line arguments for the tcb-client-l C program

Work in progress ...

## Bugs

Bound to be some bugs - especially when handling disconnections and timeouts. Let me know :-]

## Security

All the traffic that goes over the bridge in both directions is send
unencrypted. So if you are logging into the serial port of a network
switch, for example, any usernames and passwords you type will be
transmitted across the bridge as clear text.

When the bridge is between the USB to serial adapter on the laptop and a
virtual machine running on Virtual Box which is running on the same laptop
this traffic should not "escape" onto any connected networks (e.g. WiFi
and/or ethernet links). However, I won't gaurantee that so be aware.

If you don't like the sound of this then DO NOT USE THE SOFTWARE.

---------------
End of Document
