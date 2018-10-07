import socket
import os
import shutil

CS_IP = 192.168
.1
.2  # insert central server IP
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
s.bind((CS_IP, CS_PORT))
s.listen(1)

print 'connection address: ', addr

while 1:
    connection, addr = s.accept()
    request = connection.recv(BUFFER_SIZE)
dealWithUser(connection, request)


def dealWithUser(user_socket, request):
    answerUser = userRequestTPC(user_socket, request)


user_socket.send(answerUser)
user_socket.close()


def userRequestTCP(socket, request):
    splitRequest = request.split(' ')
    msgCode = splitRequest[0]  # AUT / DLU / DLR etc...
    if (msgCode == 'AUT'):
        for file in os.listdir('/CS'):
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
            #aqui deve se mesmo fazer LSU???
            sockUDP.sendto('LSU ' + user + ' ' + password)
        return 'AUR ' + status  # return answer to user

    elif (msgCode == 'DLU'):    #para haver info guardada e preciso haver uma dir do user
        if (os.path.isdir('~/'+user) == False):
            status = 'OK'
            os.remove('~/user_' + user + '.txt')    #como o user foi removido e preciso remover o fich txt
        else:
            status = 'NOK'
        return 'DLR ' + status

    elif (msgCode == 'BCK'):
        #verificar se o user ja esta no BS. para estar no BS precisa de ter um dir no CS
        if (os.path.isdir('~/'+user) == False):     #user novo por isso cria se dir no CS e um fich com os dados do BS
            sockUDP.sendto('LSU ' + user + ' ' + password)  #registar user no BS
            #recebe 'LUR status' do BS
            os.makedirs(os.path.expanduser('~/user_' + user + '/' + splitRequest[1]))
            f = open('~/user_' + user + '/' + splitRequest[1] + '/IP_port.txt', 'w')
            f.write(??IPBS?? + ' ' + ??portBS??)
            return 'BKR' + ??IPBS?? + ??portBS?? + ' '.join(splitRequest[2:])
        else:
            sockUDP.sendto('LSF ' + user + ' ' + splitRequest[1])
            #recebe 'LFD N files'
            for i in range(3, splitRequest[2]*4+2, 4):    #verifica de filename em filename
                if (splitRequest[i] != listaDoBS[i-1] or splitRequest[i+1] != listaDoBS[i] or splitRequest[i+2] != listaDoBS[i+1] or splitRequest[i+3] != listaDoBS[i+2]):
                    returnList += splitRequest[i] + splitRequest[i+1]+splitRequest[i+2]+splitRequest[i+3]
            return 'BKR '+ ??IPBS?? + ??portBS?? + splitRequest[2] + returnList

    elif (msgCode == 'RST'):    #FALTA INCLUIR O CASO EM QUE DA 'RSR EOF'
        try:
            f = open('~/user_' + user + '/' + splitRequest[1] + '/IP_port.txt', 'r')
            info = f.readlines()        #o info vai ser algo assim: ['adfsafd', 'sdfgsdg']
            return 'RSR OK'
        except:
            return 'RSR ERR'

    elif (msgCode == 'LSD'):
        reply = ''
        for dir in os.listdir('/CS/user_' + user):
            reply += ' ' + dir
            N + +
        return 'LDR ' + N + reply

    elif (msgCode == 'LSF'):
        try:
            sockUDP.sendto('LSF ' + user + splitRequest[1])
            # recebe 'LFD' por udp do bs
            splitMessage = message.split(' ')  # recebe LFD N (filename date size)*
            return 'LFD ' + BSip + ' ' + BSport + ' ' + splitMessage[1:]
        except:
            return 'LFD NOK'

    elif (msgCode == 'DEL'):
        sockUDP.sendto('DLB ' + user + splitRequest[1])
        # recebe 'DBR' por udp do bs
        splitMessage = message.split(' ')
        if (splitMessage[1] == 'OK'):
            shutil.rmtree('~/user_'+ user + '/' + splitRequest[1])  #remove a dir do user
            return 'DDR OK'
        else:
            return 'DDR NOK'


#####       UDP connection       ######
sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create socket
sock.bind((CS_IP, CS_PORT))  ##???

# receber registo de BS
while True:
    data, addrUDP = sock.recvfrom(BUFFER_SIZE)
    print 'connection asdress: ' + addrUDP
    answerBS = dealWithBS(data)
    data.send(answerBS)


def dealWithBS(data):
    splitData = data.split(' ')
    msgCode = splitData[0]
    if (msgCode == 'REG'):  # quando e que deve declinar??
        try:
            if (splitData[1] in dataBS):
                print ('O BS ja esta registado')
                return 'RGR NOK'
            else:
                dataBS[splitData[1]] = splitData[2]  # guarda se o ipBS e o portBS num dicionario
            return 'RGR OK'
        except:
            return 'RGR ERR'

    elif (msgCode == 'UNR'):  # quando e que deve declinar?
        try:
            if (splitData[1] in dataBS):
                del dataBS[splitData[1]]
                return 'UAR OK'
            else:
                return 'UAR NOK'
        except:
            return 'UAR ERR'




