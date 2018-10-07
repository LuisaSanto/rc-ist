import socket
import os

CS_IP = 192.168.1.2#insert central server IP
CS_PORT = 58001#insert

BUFFER_SIZE = 256
MESSAGE = "Server accepted connection"

#last login data
user = None
password = None

dataBS = {}








######  TCP CONECTION   #######
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((CS_IP,CS_PORT))
s.listen(1)

print 'connection address: ', addr

while  1:
    connection, addr = s.accept()
	request = connection.recv(BUFFER_SIZE)
    dealWithUser(connection, request)


def dealWithUser(user_socket, request):
	answerUser = userRequestTPC(user_socket, request)
    user_socket.send(answerUser)
	user_socket.close()


def userRequestTCP(socket, request):
    splitRequest = request.split(' ')
    msgCode = splitRequest[0]       #AUT / DLU / DLR etc...
    if (msgCode == 'AUT'):
        for file in os.listdir('/CS'):
            if (file.startswith(user+'.txt')):      #isto funciona?
                f = open('user_'+user+'.txt', "r")
                uPass = f.read()        #fica com a pass do user
                if(uPass == splitRequest[2]):
                    user = splitRequest[1]  # guardar o ultimo login
                    password = splitRequest[2]
                    status = 'OK'
                else:
                    status = 'NOK'
                break
        else:  #User novo. Para cada user criado, e tbm criado uma diretoria para o user
            user = splitRequest[1]  # guardar o ultimo login
            password = splitRequest[2]
            f = open('user_'+user+'.txt', 'w')    #cria o fich do user e vai escrever a pass
            f.write(password)
            os.makedirs(os.path.expanduser('~/'+user))      #cria o dir do user
            status = 'NEW'
            sockUDP.sendto()
            #enviar por UDP 'LSU '+user+' '+password ao bs
        return 'AUR ' + status     #return answer to user

    elif (msgCode == 'DLU'):
        ///find user info stored///
        if (///find user info stored in BS/// == false):  #se nao houver dir no BServer
            status = 'OK'
        else:
            status = 'NOK'
        return 'DLR ' + status

    elif (msgCode == 'BCK'):
        dir = splitRequest[1]
        n = int(splitRequest[2])
        sockUDP.sendto('LSU ' + user + ' ' + password)          #e necessario o bs fazer backup por isso o bs precisa de registar o user
        
        ///TO_DO///
        return 'BKR' +

    elif (msgCode == 'RST'):

        return 'RSR' +

    elif (msgCode == 'LSD'):
        reply = ''
        for dir in os.listdir('/CS/user_' + user):
            reply += ' ' + dir
            N++
        return 'LDR ' + N + reply

    elif (msgCode == 'LSF'):
        #envia 'LSF'+splitRequest[1] por udp ao bs
        #recebe 'LFD' por udp do bs
        splitMessage = message.split()      #recebe LFD N (filename date size)*
        return 'LFD ' + BSip + ' ' + BSport + ' ' + splitMessage[1:]

    elif (msgCode == 'DEL'):
        #envia DLB user splitRequest[1] por udp ao bs
        #recebe 'DBR' por udp do bs
        splitMessage = message.split()
        if (splitMessage[1] == 'OK'):




#####       UDP connection       ######
sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create socket
sock.bind((CS_IP, CS_PORT)) ##???

#receber registo de BS
while True:
    data, addrUDP = sock.recvfrom(BUFFER_SIZE)
    print 'connection asdress: ' + addrUDP
    answerBS = dealWithBS(data)
    data.send(answerBS)

def dealWithBS(data):  ['asdf','fdsafd','asdfad']
    splitData = data.split(' ')
    msgCode = splitData[0]
    if (msgCode == 'REG'):          #quando e que deve declinar??
        try:
            if (splitData[1] in dataBS):
                print ('O BS ja esta registado')
                return 'RGR NOK'
            else:
                dataBS[splitData[1]] = splitData[2]         #guarda se o ipBS e o portBS num dicionario
            return 'RGR OK'
        except:
            return 'RGR ERR'

    elif(msgCode == 'UNR'):         #quando e que deve declinar?
        try:
            if (splitData[1] in dataBS):
                del dataBS[splitData[1]]
                return 'UAR OK'
            else:
                return 'UAR NOK'
        except:
            return 'UAR ERR'

