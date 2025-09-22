#! /usr/bin/python3
#
# @(!--#) @(#) tcb-server-w.py, sversion 0.1.0, fversion 007, 22-september-2025
#
# TCP to COM bridge server (Python 3 on Windows 10/11)
#
# Links:
#    https://stackoverflow.com/questions/7749341/basic-python-client-socket-example
#    https://readmedium.com/how-to-poll-sockets-using-python-3e1af3b047
#

##############################################################################

#
# imports
#

import sys
import os
import argparse
import time
import subprocess
import socket
import select
import serial
import serial.tools.list_ports

##############################################################################

#
# globals
#

DEFAULT_DEBUG_LEVEL       = 1
DEFAULT_COM               = '-'
DEFAULT_BAUD              = '9600'
DEFAULT_BIND_IPV4         = '-'
DEFAULT_BIND_TCP_PORT     = '8089'
DEFAULT_TIMEOUT           = 0.01

BUFFER_SIZE               = 8192

debug = DEFAULT_DEBUG_LEVEL

##############################################################################

def availablecomports():
    comports = []
    
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        comport = port.device
        
        if len(comport) < 4:
            continue
        
        if len(comport) > 6:
            continue

        if comport[0:3] != 'COM':
            continue
        
        if not comport[3:].isdigit():
            continue
        
        comports.append(comport.upper())
                    
    return comports

##############################################################################

def process_connection(connection, address, servercom, timeout):
    global progname
    
    print('Starting bridge loop')
    
    while True:
        # print('Reading from serial COM port')
        received = servercom.read(BUFFER_SIZE)
         
        if len(received) > 0:
            if debug == 2:
                print('A total of {} bytes read from the COM port - sending to {}.{}'.format(len(received), address[0], address[1]))

            if debug == 1:
                for i in range(0, len(received)):
                    print('<', end='', flush=True)

            connection.send(received)
        else:
            # print('No bytes on COM port')
            pass
            
        rlist, wlist, xlist = select.select([connection], [], [], timeout)
        
        if ((len(rlist) == 0) and (len(wlist) == 0) and (len(xlist) == 0)):
            # print('No bytes to read on connection address {}'.format(address))
            pass
        else:
            if len(rlist) > 0:
                if debug == 2:
                    print('Bytes available to read on connection - reading them now')

                received = connection.recv(BUFFER_SIZE)
                
                numreceived = len(received)
                
                if numreceived == 0:
                    # the socket being ready but there not being any data is a sign the connnection has dropped
                    print('')
                    print('No bytes read from socket - assuming connection has dropped')
                    break
                else:
                    if debug == 2:
                        print('{} bytes read from socket - writing them to com port'.format(numreceived))

                    if debug == 1:
                        for i in range(0, numreceived):
                            print('>', end='', flush=True)

                    servercom.write(received)

    # close the connection
    connection.close()
    

    return 0        

##############################################################################

def main():
    global progame
    global debug

    parser = argparse.ArgumentParser()
        
    parser.add_argument('--debug',   help='debug level',             default=DEFAULT_DEBUG_LEVEL)
    parser.add_argument('--com',     help='COMn port name',          default=DEFAULT_COM)
    parser.add_argument('--baud',    help='baud rate',               default=DEFAULT_BAUD)
    parser.add_argument('--bind',    help='IPv4 address to bind to', default=DEFAULT_BIND_IPV4)
    parser.add_argument('--port',    help='TCP port to bind to',     default=DEFAULT_BIND_TCP_PORT)
    parser.add_argument('--timeout', help='timeout',                 default=DEFAULT_TIMEOUT)

    args = parser.parse_args()

    debug = int(args.debug)
    
    comport = args.com.upper()
    
    if comport == DEFAULT_COM:
        comports = availablecomports()
        
        if len(comports) == 0:
            print('{}: no COM ports available - is a USB to serial converter plugged in?'.format(progname), file=sys.stderr)
            sys.exit(1)
        elif len(comports) == 1:
            comport = comports[0]
        else:
            highest = 0
            
            for i in range(0, len(comports)):
                ### print(int(comports[i][3:]))
                if int(comports[i][3:]) > highest:
                    highest = int(comports[i][3:])
                    comport = comports[i]

            print('{}: multiple COM ports available:'.format(progname), end='', file=sys.stderr)
            for c in comports:
                print(' {}'.format(c), end='', file=sys.stderr)
            print(': selected {}'.format(comport), file=sys.stderr)
            
    bind = args.bind
    
    if bind == DEFAULT_BIND_IPV4:
        ipconfig_output = subprocess.check_output('ipconfig', shell=True, text=True)        
        
        ipconfig_lines = ipconfig_output.split('\n')
        
        linenum = 0
        for ipconfig_line in ipconfig_lines:
            linenum += 1
            
            words = ipconfig_line.split()
            
            if len(words) >= 3:
                if (words[0] == 'IPv4') and (words[1].startswith('Address')):
                    ipv4 = words[-1]
                    
                    if ipv4.startswith('10.'):
                        bind = ipv4
                        break

        if bind == DEFAULT_BIND_IPV4:
            print('{}: unable to automatically determine a candidate BIND IPv4 address'.format(progname), file=sys.stderr)
            sys.exit(1)
    
    print('COM ...........: {}'.format(comport))
    print('Baud ..........: {}'.format(args.baud))
    print('BIND IPv4 .....: {}'.format(bind))
    print('BIND port .....: {}'.format(args.port))
    print('Timeout .......: {}'.format(args.timeout))

    print('Opening serial port {} at baud rate {}'.format(comport, args.baud))
    try:
        servercom = serial.Serial(comport, int(args.baud), timeout=float(args.timeout))
    except serial.serialutil.SerialException:
        print('{}: problem opening COM port "{}"'.format(progname, comport), file=sys.stderr)
        sys.exit(1)    

    print('Creating a TCP (stream) based socket')
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print('Binding socket to IPv4 {} on port {}'.format(bind, args.port))
    try:
        serversocket.bind((bind, int(args.port)))
    except OSError:
        print('{}: problen trying to bind socket to IPv4 {} - is the bind IPv4 address correct?'.format(progname, bind), file=sys.stderr)
        exit(1)
    
    print('Setting socket to listen mode')    
    serversocket.listen(5)

    while True:
        print('Waiting for a TCP/IP incoming connection')
        
        connection, address = serversocket.accept()
        
        print('Connection received from {}:{}'.format(address[0], address[1]))
        
        process_connection(connection, address, servercom, float(args.timeout))
        
        print('Connection dropped - looping')
        
        time.sleep(1.0)


##############################################################################

progname = os.path.basename(sys.argv[0])

sys.exit(main())

# end of file
