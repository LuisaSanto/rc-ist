import socket
import sys
import argparse
import os as os
from os import listdir
from os.path import isfile, join
import shutil
from multiprocessing import Barrier, Lock, Process


#TODO: check open file codes + python manager

def receive_file(socketAccept, user_name, user_dir):
    file_size = ""
    create_dir_name = os.path.dirname("/" + user_name)
    if not os.path.exists(create_dir_name):
        os.makedirs(create_dir_name)

    try:
        byte = socketAccept.recv(1)
        while byte != "":
            file_size += byte
            byte = socketAccept.recv(1)
        print("File size is {}".format(file_size))
        file_size = eval(file_size)
        try:
            os.remove("/" + user_name + "/" + user_dir)
            print("Files overwritten")
        except:
            print("File created")
        file_received = open("/" + user_name + "/" + user_dir, "wb+")
        try:
            while file_size > 0:
                socketAccept.settimeout(10)
                data = socketAccept.recv(256)
                file_size -= len(data)
                if file_size <= 0 and data[-1] == "\n":
                    data = data[:-1]
                elif file_size <= 0 and data[-1] != "\n":
                    print("File size is too small. Exit")
                file_received.write(data)
        except:
            print("RBR ERR\n")
            print("Error receiving message from Central Server")
            socketAccept.send("RBR ERR\n")
            return
        file_received.close()
    except:
        print("RBR ERR\n")
        print("Error receiving file from Central Server")
        socketAccept.send("RBR ERR\n")




def send_file(socketAccept, user_name, user_dir, user_n):
    path = user_name + "/" + user_dir
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    time = []
    size = []
    for file in onlyfiles:
        files_path = path + "/" + file
        size += [os.path.getsize(files_path)]
        time += [time.ctime(os.path.getmtime(files_path))]  # TODO: DATE FORMAT
    print("Sending files to user")
    try:
        for i in range(user_n):
            file_to_user = open(onlyfiles[i], "rb")
            data = file_to_user.read(256)
            while(data):
                socketAccept.send(data)
                details = size[i] + time[i]
                socketAccept.send(details)
    except socket.error as err:
        print("UPR ERR\n")
        print("Error sending message to Central Server: {}".format(err))
        socketAccept.send("UPR ERR\n")
        return

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


def servingCS(socketUDP):
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
            update_users()
        except IOError as err:
            print("Error trying to remove user from BS")
            serverUDP.sendto("DBR ERR\n")
            return

        print("Removal completed")
        update_users()
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


def servingUser(serverTCP):
    while 1:
        try:
            print("Waiting for a user to contact")
            socketAccept, address = serverTCP.accept()
            user_name = ""
            print("Connection received from  {}".format(address))
            try:
                message = socketAccept.recv(1024) #read the frist 3 bytes
            except:
                print("Error receiving message")
                return
            reply = message.split(' ')
            if message == "":
                print("Empty message")

            elif message[:3] == "AUT":
                if len(reply) != 3:
                    print("ERR! Message sent from server is corrupted")
                    try:
                        socketAccept.send("AUT ERR\n")
                    except socket.error as err:
                        print("Error sending message to client")
                        return
                user_name = reply[1]
                user_pw = reply[2]
                user = user_name + " " + user_pw
                users_dict = update_users()
                if users_dict.get(user_name):
                    print("User already registered, updating password")
                    try:
                        users_file = open("users.txt", "r")
                        lines = users_file.readlines()
                        users_file.close()
                        for i in range(len(lines)):
                            if user_name in lines[i]:
                                del lines[i]
                                break
                        users_file = open("users.txt", "w")
                        lines.append(user)
                        for line in lines:
                            users_file.write(line)
                        users_file.close()
                        update_users()
                    except IOError as err:
                        print("Error trying to remove user from BS")
                        socketAccept.send("AUR ERR\n")
                        return
                else:
                    print("Registering new user")
                    try:
                        users_file = open("users.txt", "r")
                        lines = users_file.readlines()
                        users_file.close()
                        users_file = open("users.txt", "w")
                        lines.append(user)
                        for line in lines:
                            users_file.write(line)
                        users_file.close()
                        update_users()
                    except IOError as err:
                        print("Error trying to remove user from BS")
                        socketAccept.send("AUR ERR\n")
                        return
                try:
                    socketAccept.send("AUR OK\n")
                except socket.error as err:
                    print("AUR ERR\n")
                    print("Error sending message to Central Server: {}".format(err))
                    socketAccept.send("AUR ERR\n")
                    return

            elif message[:3] == "UPL":
                if len(reply) != 3:
                    print("ERR! Message sent from server is corrupted")
                    try:
                        socketAccept.send("UPR ERR\n")
                    except socket.error as err:
                        print("Error sending message to client")
                        return
                user_dir = reply[1]
                user_n = reply[2]
                send_file(socketAccept, user_name, user_dir, user_n)
                try:
                    socketAccept.send("UPR OK\n")
                except socket.error as err:
                    print("UPR ERR\n")
                    print("Error sending message to Central Server: {}".format(err))
                    socketAccept.send("UPR ERR\n")
                    return
            elif message[:3] == "RSB":
                if len(reply) != 2:
                    print("ERR! Message sent from server is corrupted")
                    try:
                        socketAccept.send("UPR ERR\n")
                    except socket.error as err:
                        print("Error sending message to client")
                        return
                user_dir = reply[1]
                receive_file(socketAccept, user_name, user_dir)
                try:
                    socketAccept.sendto("RBR OK\n")
                except socket.error as err:
                    print("RBR ERR\n")
                    print("Error sending message to Central Server: {}".format(err))
                    socketAccept.send("RBR ERR\n")
                    return
            else:
                print("Message received with wrong format")
                return
        finally:
            socketAccept.close()


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
    portCS = 58001
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
        try:
            message = "REG " + socket.gethostbyname(socket.gethostname()) + \
                      " " + str(portBS) + "\n"
            print("Sending registation message to CS on host and port: {}".format(
                (socket.gethostbyname(hostCS), portCS)
            ))
            print (socket.gethostbyname(hostCS))
            serverUDP.sendto(message.encode(), (socket.gethostbyname(hostCS), portCS))
        except socket.error as err:
            print("RGR ERR")
            print("Error sending message to Central Server: {}".format(err))
            sys.exit("Shutting down Backup Server")

        print("Waiting for CS confirmation")
        try:
            serverUDP.settimeout(10)
            #serverUDP.bind((hostCS, portCS))
            confirmation = serverUDP.recvfrom(1024)
            print(confirmation.decode())
        except:
            print("Timeout exceeded!")
            print("Confirmation not possible. Closing server")
            sys.exit("Shutting down Backup Server.")

        if confirmation[0] == "REG NOK\n":
            print("Registation not possible. Closing server")
            serverUDP.close()
            sys.exit()

        print("Registation completed with success")


    except:
        print("Backup Server not responding. Try again.")
        sys.exit("Shutting down Backup Server.")

    isRegisted = 1

    synchronizer = Barrier(2)
    serializer = Lock()
    process_cs = Process(target = servingCS, args=(serverUDP, portCS))  # TODO: multiprocessing this function
    process_cs.daemon = True #run process_cs as daemon so it termates with the main process
    process_cs.start()
    ##########################################################################################################
    ##########################################################################################################
    ######################## create a tcp socket to establish user connection ################################
    ##########################################################################################################
    ##########################################################################################################

    serverTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverTCP.bind((hostCS, portBS))
    serverTCP.listen(5)

    # process_user = Process(target=servingUser, args=(serverTCP,))  # TODO: multiprocessing this function maybe
    servingUser(serverTCP)
    # process_user.daemon = True
    # process_user.start()


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
