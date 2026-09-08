# A program to create a bridge between a Windows desktop's USB serial COM port and a TCP endpoint

## Warning!!!

Please read the security section. In summary: everything sent across the
"bridge" in both directions is sent `unencrypted`.

USE AT YOUR OWN RISK!!!

## Security

All the traffic that goes over the bridge in both directions is sent
unencrypted. For example, if you are logging into the serial port of a network
switch then any usernames and passwords you type will be
transmitted across the bridge as clear text.

When the bridge is between the USB to serial adapter on the Windows
machine and a virtual machine running on Virtual Box which is running on
the same Windows machine then this traffic should not "escape" onto any
connected networks (e.g. WiFi and/or ethernet links).

However, it would be wrong of me to guarantee that bridge traffic will
never escape so beware!

If you don't like the sound of this then DO NOT USE THE SOFTWARE!!!

## Abstract

This bridge program was written to overcome an issue I was having trying
to get an Ubuntu 24.04 LTS virtual machine which runs under Virtual
Box on my Windows 10 (soon to be Windows 11) laptop to talk to a USB
serial adapter.

First I tried connecting a USB serial adapter to one of the laptops USB
ports and, within Virtual Box, mapping the USB device to the virtual
machine. The USB serial adtapter could be seen on the Ubuntu machine
as device file /dev/ttyUSB0 and trying to use this device file would initially work. However, the device would soon hang
and/or become otherwise unreliable.

Sometimes the Ubuntu virtual machine would not restart properly.

Some googling shows other people have had issues with mapping USB to serial
adaptors in Virtual Box.

Rather than try the many workarounds suggested on the internet
I have taken a different approach.

I have a Python 3 program called `tcp-com-bridge.py` that works
as a bridge between the USB
serial adapter in Windows and a TCP endpoint.

On the Ubuntu virtual machine hosted by Virtual Box I use another program
called `autoserial` to connect to the TCP endpoint. The `autoserial`
program is available to download from here:
    
[Connect to a local serial device or a TCP to COM serial bridge](https://codeberg.org/andycranston/autoserial)

## My setup

Here is a diagram showing my particular set up:

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

I have a laptop running Oracle Virtual Box. Oracle Virtual Box
is hosting a virtual machine instance running the Ubuntu 24.04 LTS
operating system.

Connected to one of the laptops USB ports is a USB serial adapter.

A RJ45 to DB9 cable is use to connect to the serial device. The DB9 end plugs
into the USB serial adapter and the RJ45 end plugs into the serial device
(in this setup a Cisco C2950 network switch).

# Quick start

Copy the `tcp-com-bridge.py` Python 3 program to the Windows laptop.

Open a command prompt and change to the directory that the
`tcp-com-bridge.py` program was copied to.

Run the program with:

```
python tcp-com-bridge.py --bind 10.7.0.10 --baud 9600
```

Change the IP address to the IP address of the laptop.

Login into the Ubuntu 24.04 LTS virtual machine.

From this webpage:
    
[Connect to a local serial device or a TCP to COM serial bridge](https://codeberg.org/andycranston/autoserial)

download and compile the `autoserial` program.

Now run the `autoserial` program as:

```
autoserial 10.7.0.10 8089
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

and the `autoserial` program will terminate.

## Command line arguments for the tcp-com-bridge.py Python program

### The --com command line argument

The `--com` command line argument can be used to specify which COM port
on the Windows machine open.

If there is only one COM port available the `--com` command line argument
is not necessary as the program will determine the name of the single
COM port.

If the `--com` command line argument is not specified and there are two
or more COM ports available on the Windows machine then the one with
the highest number will be used. For example if the following COM ports
are available:

```
COM1   COM2   COM14
```

then COM14 will be used.

### The --baud command line argument

The baud rate to open the COM port at defaults to 9600 baud. To specify
a different baud rate use the `--baud` command lne argument. For example
to use baud rate 115200 run the `tcp-com-bridge.py` program as follows:

```
python tcp-com-bridge.py --baud 115200
```
### The --bind command line argument

The `--bind` command line agument is used to specify the IPv4 address that
the `tcp-com-bridge.py` program should listen on for incomining connections.

If the `--bind` command line agument is omitted the `tcp-com-bridge.py`
program will see if there are any interfaces which have an IPv4 address
where the first two octets are 10 and 7 such as:

```
10.7.0.10
```

This is a hack to match my own test networks and save me, the program
author, some typing :-]

### The --port command line argument

The `--port` command line argument is used to specifiy the TCP/IP port
number the `tcp-com-bridge.py` should listen on.

It defaults to port 8089 but if a different port number is needed it
can be specified. For example:

```
python tcp-com-bridge.py --port 9123
```

### The --timeout command line argument

The `--timeout` command line argument should never really be required
but is included for experimentation and testing.

The value is a floating point number which defaults to 0.01 seconds. This
is the time to wait for input to arrive on both the COM port and the
TCP/IP port. Smaller values will make the program more responsive at
the expense of extra CPU cycles. Larger numbers will make the program
"laggy" to the point of unusability.

Depending on your hardware specifications you might want to try different
values but 0.01 seconds (i.e. one hundredth of a second) has, so far,
been satisfactory.

## Bugs

Bound to be some bugs - especially when handling disconnections and
timeouts. Let me know - my email address is:
    
```
andy [at] cranstonhub [dot] com
```

----------------
End of README.md
