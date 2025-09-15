# Two programs to create a bridge between a Windows desktop's USB serial COM port and a Linux server

## Warning!

Please read the security section. In summary everything sent across the
"bridge" in both directions is sent un-encrypted.

USE AT YOUR OWN RISK!!!

## Abstract

The programs here were written to overcome an issue I was having trying to
get an Ubuntu 24.04 LTS virtual machine which runs under Virtual Box
on my Windows 10 (soon to be Windows 11) laptop.

When I connected a USB to serial
adapter to one of the laptops USB ports I could map the USB device ok and see
it on the Ubuntu machine as /dev/ttyUSB0 but trying to use it would initially
work but then hang and/or become otherwise unreliable.

Sometimes the Ubuntu virtual machine would not restart properly.

Some googling shows other people have had issues with USB to serial adaptors
and Virtual Box.

Rather than try the many workarounds suggested I have taken a different approach.

I have written two programs that work as a bridge between the USB to serial adapter in Windows
and the Ubuntu virtual machine hosted by Virtual Box.

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

Open a command prompt and change to the directory that  `tcb-server-w.py` was copied to.

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

Work in progress ...

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
