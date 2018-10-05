import socket
import sys
import argparse

try:
    # parse input
    parser = argparse.ArgumentParser()

    parser.add_argument("-b", help="Backup Server port", type=int)
    parser.add_argument("-n", help="Central Server host")
    parser.add_argument("-p", help="Central Server port", type=int)

    try:
        arguments = parser.parse_args()
    except:
        print("Error in format")
        print("Try:-b 59000 -n tejo.ist.utl.pt -p 58001")
        sys.exit(0)

    # Default values
    hostCS = socket.gethostbyname()
    portCS = 59001
    portBS = 59000

    # parse inserted args
    if arguments.b: portBS = arguments.b
    if arguments.n: hostCS = arguments.n
    if arguments.p: portCS = arguments.p

    #####################################################
    # create a tcp socket to establish user connection
    #####################################################

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((hostCS, portBS))
    server.listen(5)
    # TODO: TCP functions

except KeyboardInterrupt:
    print('\n KeyboardInterrupt found')

except socket.error:
    print("Socket error found. Aborting!")

finally:
    # TODO: VER DISTO
    sys.exit(0)
