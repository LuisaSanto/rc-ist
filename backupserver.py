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
    # create a udp socket to establish CS connection
    #####################################################

    serverUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # TODO: settimeout
        # BS registation on CS
        message = "REG " + socket.gethostbyname(socket.gethostname()) + \
                  " " + str(portBS) + "\n"
        print("Sending registation message to CS on host and port: {}".format(
            (socket.gethostbyname(hostCS), portBS)
        ))
        try:
            serverUDP.sendto(message, (socket.gethostbyname(hostCS), portBS))
        except socket.error as err:
            print("RGR ERR")
            print("Error sending message to Central Server: {}".format(err))
            sys.exit("Shutting down Backup Server")

        print("Waiting for CS confirmation")
        try:
            serverUDP.settimeout(100)
            confirmation = serverUDP.recvfrom(1024)
        except:
            print("Timeout exceeded!")
            print("Confirmation not possible. Closing server")
            sys.exit("Shutting down Backup Server.")

        if (confirmation[0] == "REG NOK\n"):
            print("Registation not possible. Closing server")
            serverUDP.close()
            sys.exit()

        print("Registation completed with success")
        isRegisted = 1

    except:
        print("Backup Server not responding. Try again.")
        sys.exit("Shutting down Backup Server.")

    #####################################################
    # create a tcp socket to establish user connection
    #####################################################

    serverTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverTCP.bind((hostCS, portBS))
    serverTCP.listen(5)
    # TODO: TCP functions

except KeyboardInterrupt:
    print('\n KeyboardInterrupt found')

except socket.error:
    print("Socket error found. Aborting!")

finally:
    # TODO: VER DISTO
    if (isRegisted == 1):
        message = "UNR " + socket.gethostbyname(socket.gethostname()) + \
                  str(portBS)
        print("Sending termination connection to: {}".format(
            (socket.gethostbyname(hostCS), portBS)
        ))
        try:
            serverUDP.sendto(message, (socket.gethostbyname(hostCS), portBS))
        except socket.error as err:
            print("BKR ERR")
            print("Error sending message to Central Server: {}".format(err))
            sys.exit("Shutting down Backup Server")
        print("Waiting for CS confirmation")

        try:
            serverUDP.settimeout(10)
            confirmation = serverUDP.recvfrom(1024)
        except:
            print("Timeout exceeded!")
            print("Registation not possible. Closing server")
            sys.exit("Shutting down Backup Server.")
        if (confirmation[0] == "UAR NOK"):
            print("Registation not possible. Closing server")
            serverUDP.close()
            sys.exit()
        print("Unregistation completed with success")
        serverUDP.close()
    print("Shutting down Backup Server")
    sys.exit(0)
