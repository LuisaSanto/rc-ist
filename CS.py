import socket
import os
import shutil

CS_IP = socket.gethostbyname('douro')  # insert central server IP
CS_PORT = 58001  # insert

BUFFER_SIZE = 256
MESSAGE = "Server accepted connection"

# last login data
user = None
password = None

dataBS = {}
returnList = []

######  TCP CONECTION   #######
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((CS_IP, CS_PORT))
s.listen(1)

print 'running'


def userRequestTCP(socket, request):
    splitRequest = request.split(' ')
    msgCode = splitRequest[0]  # AUT / DLU / DLR etc...
    if (msgCode == 'AUT'):
        print (splitRequest[1], splitRequest[2])
        for file in os.listdir('.'):
            if (file.startswith(user + '.txt')):  # isto funciona?
                f = open('user_' + user + '.txt', "r")
                uPass = f.read()  # fica com a pass do user
                if (uPass == splitRequest[2]):
                    user = splitRequest[1]  # guardar o ultimo login
                    password = splitRequest[2]
                    status = 'OK'
                else:
                    status = 'NOK'
                break
        else:  # User novo. Para cada user criado, e tbm criado uma diretoria para o user
            user = splitRequest[1]  # guardar o ultimo login
            password = splitRequest[2]
            f = open('user_' + user + '.txt', 'w')  # cria o fich do user e vai escrever a pass
            f.write(password)
            os.makedirs(os.path.expanduser('~/user_' + user))  # cria o dir do user
            status = 'NEW'
        return 'AUR ' + status  # return answer to user

def dealWithUser(user_socket, request):
    answerUser = userRequestTCP(user_socket, request)
    user_socket.send(answerUser)
    user_socket.close()

while 1:
    connection, addr = s.accept()
    print 'connection address: ', addr
    request = connection.recv(BUFFER_SIZE)
    print 'request: ', request
    dealWithUser(connection, request)
