import socket
import sys
import argparse
import os as os
from os import listdir
from os.path import isfile, join
import shutil


def update_users():
        users_file = open("users.txt", "r")
        user_lines = users_file.readlines()
        users = []
        pw = []
        for i in range(len(user_lines)):
            pair = user_lines[i].split(" ")
            users += [pair[0]]
            pw += [pair[1].rstrip()]
        return dict(zip(users, pw))

def servingCS(socketUDP, portUDP):
    print("Awaiting contact from CS")
    try:
        socketUDP.settimeout(300.0)
        message, address = socketUDP.recvfrom(1024)
    except Exception:
        print("5 minutes have passed. Waiting 5 more minutes.")
        return
    reply = message.split(' ')
    print("Message received from {]".format(address[0], str(address[1])))
    print("Content: {}".format(message))

    if message[:3] == "LSF":
        if len(reply) != 3:
            print("ERR! Message sent from server is corrupted")
            try:
                serverUDP.sendto("LFD ERR\n")
            except socket.error as err:
                print("Error sending message to client")
                return
        user_name = reply[1]
        user_dir = reply[2]
        print("Getting user's name directory")
        users_dict = update_users()
        if users_dict.get(user_name):
            path = user_name + "/" + user_dir
            onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
            time = []
            size = []
            for file in onlyfiles:
                files_path = path + "/" + file
                size += [os.path.getsize(files_path)]
                time += [time.ctime(os.path.getmtime(files_path))]  # TODO: DATE FORMAT
            print("Sending LSF reply message")
            try:
                merge_list = list(zip(onlyfiles, time, size))
                serverUDP.sendto("LFD" + len(onlyfiles) + merge_list)
            except socket.error as err:
                print("LFD ERR\n")
                print("Error sending message to Central Server: {}".format(err))
                serverUDP.sendto("LFD ERR\n")
                return
        else:
            print("User not found.")
            serverUDP.sendto("LFD ERR\n")
            
    elif message[:3] == "LSU":
        if len(reply) != 3:
            print("ERR! Message sent from server is corrupted")
            try:
                serverUDP.sendto("LUR ERR\n")
            except socket.error as err:
                print("Error sending message to client")
                return
        user_name = reply[1]
        user_pw = reply[2]
        user = user_name + " " + user_pw
        print("Adding new user to user's list")
        users_file = open("users.txt", "a")
        users_file.write(user)
        users_file.close()
        try:
            serverUDP.sendto("LUR OK\n")
        except socket.error as err:
            print("LUR ERR\n")
            print("Error sending message to Central Server: {}".format(err))
            serverUDP.sendto("LUR ERR\n")
            return


    elif message[:3] == "DLB":
        if len(reply) != 3:
            print("ERR! Message sent from server is corrupted")
            try:
                serverUDP.sendto("DBR ERR\n")
            except socket.error as err:
                print("Error sending message to client")
                return
        user_name = reply[1]
        user_dir = reply[2]
        user = user_name + " " + user_dir

        print("Removing user's directory")
        try:
            shutil.rmtree(user)
        except Exception as err:
            print("Error in removing user directory")
            socketUDP.sendto("DBR NOK\n")
            return

        print("Removing user in user's list")
        try:
            users_file = open("users.txt", "r")
            lines = users_file.readlines()
            users_file.close()
            for i in range(len(lines)):
                if user_name in lines[i]:
                    del lines[i]
                    break
            users_file = open("users.txt", "w")
            for line in lines:
                users_file.write(line)
            users_file.close()
        except IOError as err:
            print("Error trying to remove user from BS")
            serverUDP.sendto("DBR ERR\n")
            return

        print("Removal completed")
        try:
            serverUDP.sendto("DLB OK\n")
        except socket.error as err:
            print("DBR ERR\n")
            print("Error sending message to Central Server: {}".format(err))
            serverUDP.sendto("DBR ERR\n")
            return

    else:
        print("Message received with wrong format")
        return


try:
    isRegisted = 0

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
    hostCS = socket.gethostname()
    portCS = 59001
    portBS = 59000

    # parse inserted args
    if arguments.b: portBS = arguments.b
    if arguments.n: hostCS = arguments.n
    if arguments.p: portCS = arguments.p


    ##########################################################################################################
    ##########################################################################################################
    ######################## create a udp socket to establish CS connection ##################################
    ##########################################################################################################
    ##########################################################################################################

    serverUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
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


    except:
        print("Backup Server not responding. Try again.")
        sys.exit("Shutting down Backup Server.")

    isRegisted = 1

    servingCS(serverUDP, portBS)

    # TODO: KEEP HERE


    ##########################################################################################################
    ##########################################################################################################
    ######################## create a tcp socket to establish user connection ################################
    ##########################################################################################################
    ##########################################################################################################

    serverTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverTCP.bind((hostCS, portBS))
    serverTCP.listen(5)
    # TODO: TCP functions


# Exceptions treatment
except KeyboardInterrupt:
    print('\n KeyboardInterrupt found')

except socket.error:
    print("Socket error found. Aborting!")

finally:
    # BS unregistation on CS
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
