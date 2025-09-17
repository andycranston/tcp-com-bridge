#
# @(!--#) @(#) tcp-client-w.py, version 002, 17-september-2025
#
# a simple serial terminal emulator which connects to the tcp-com bridge server
#
# Platform is Windows only for two reasons:
#   (1) it uses msvcrt console I/O keyboard functions
#
# Links:
#
#    https://docs.python.org/3/howto/argparse.html
#    https://docs.python.org/3.7/library/msvcrt.html
#

##############################################################################

#
# imports
#

import sys
import os
import argparse
import time
import socket
import select
import msvcrt

##############################################################################

#
# globals
#

# DEFAULT_IPV4         = '10.7.0.10'
DEFAULT_IPV4         = '10.7.2.180'
DEFAULT_TCP_PORT     = '8089'
DEFAULT_TIMEOUT      = 0.1

BUFFER_SIZE          = 8192

##############################################################################

def bridgeterminal(clientsocket):
    ba = bytearray(1)

    while True:
        rlist, wlist, xlist = select.select([clientsocket], [], [], DEFAULT_TIMEOUT)
        
        if ((len(rlist) == 0) and (len(wlist) == 0) and (len(xlist) == 0)):
            pass
        else:
            if len(rlist) > 0:
                received = clientsocket.recv(BUFFER_SIZE)

                if len(received) > 0:
                    for i in range(0, len(received)):
                        c = received[i]

                        if (c >= 32) and (c <= 126):
                            print(chr(c), end='', flush=True)
                        elif c == 8:
                            print('\b', end='', flush=True)
                        elif c == 9:
                            print('  <tab>  ', end='', flush=True)
                        elif c == 10:
                            print('', flush=True)
                        elif c == 13:
                            print('\r', end='', flush=True)
                        else:
                            print('[{:02X}]'.format(c), end='', flush=True)

            
        # read characters
        while msvcrt.kbhit():
            c = msvcrt.getch()
            
            # print(c, '   ', type(c))
                        
            clientsocket.send(c)

##############################################################################

def main():
    global progame

    parser = argparse.ArgumentParser()
        
    parser.add_argument('--ipv4',
                        help='IPv4 address to connect to',
                        default=DEFAULT_IPV4)
                        
    parser.add_argument('--port',
                        help='TCP port to connect on',
                        default=DEFAULT_TCP_PORT)

    parser.add_argument('--timeout',
                        help='timeout',
                        default=DEFAULT_TIMEOUT)

    args = parser.parse_args()
    
    print('IPv4 .....: {}'.format(args.ipv4))
    print('port .....: {}'.format(args.port))
    
    print('Creating TCP (stream) socket')
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print('Connecting to {}:{}'.format(args.ipv4, args.port))
    clientsocket.connect((args.ipv4, int(args.port)))
    
    print('Connected')
 
    try:
        bridgeterminal(clientsocket)
    except KeyboardInterrupt:
        print('')
        print('<<Exiting>>')
    except ConnectionAbortedError:
        print('')
        print('<<Remote bridge disconnected>>')
        
        
    return 0

##############################################################################

progname = os.path.basename(sys.argv[0])

sys.exit(main())

# end of file
