import socket
import os
import shutil
import select

CS_IP = socket.gethostbyname()
CS_PORT = 58001

BUFFER_SIZE = 256
MESSAGE = "Server accepted connection"

# last login data
user = ''
password = ''

dataBS = {}
returnList = []


print 'running'

def dealWithUser(request):
    global user
    global password
    splitRequest = request.split(' ')
    msgCode = splitRequest[0]  # AUT / DLU / DLR etc...
    if (msgCode == 'AUT'):
        for file in os.listdir('.'):        #lista os fichs na diretoria /CS
            if (file == user + '.txt'):
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
            os.makedirs(os.path.expanduser('/CS/user_' + user))  # cria o dir do user
            status = 'NEW'
        return 'AUR ' + status + '\n' # return answer to user

    elif (msgCode == 'DLU'):    #para haver info guardada e preciso haver uma dir do user
        if len(os.listdir('/CS' + user)) == 0:  #verificar se a dir do user esta vazia
            status = 'OK'
            os.remove('/CS/user_' + user + '.txt')  #remover o fich user e a sua dir
            os.remove('/CS/user_' + user)
        else:
            status = 'NOK'
        return 'DLR ' + status + '\n'

    elif (msgCode == 'BCK'):
        #estou a supor que para cada user, cada dir e guardada por um bs unico
        #verificar se o user ja tem info no BS -> precisa de ter uma dir com o ip do BS
        if len(os.listdir('/CS/user_' + user)) == 0:
            # user novo por isso cria se dir no CS e um fich com os dados do BS
            serverUDP.sendto('LSU ' + user + ' ' + password, SERVER_SOCKET)  #registar user no BS
            #recebe 'LUR status' do BS
            ###   TODO  ###
            os.makedirs(os.path.expanduser('/CS/user_' + user + '/' + splitRequest[1]))
            f = open('/CS/user_' + user + '/' + splitRequest[1] + '/IP_port.txt', 'w')
            f.write(??IPBS?? + ' ' + ??portBS??)
            return 'BKR' + ??IPBS?? + ??portBS?? + ' '.join(splitRequest[2:]) + '\n'

        elif (os.path.isdir("/CS/user_" + user + '/' + splitRequest[1])) == False:
            #user que ja tem dir mas e diferente daquela onde vai fazer o backup
            #serverUDP.sendto('LSU ' + user + ' ' + password, SERVER_SOCKET)  # registar user no BS
        else:
            serverUDP.sendto('LSF ' + user + ' ' + splitRequest[1], SERVER_SOCKET)
            #recebe 'LFD N files'
            ###   TODO  ###
            for i in range(3, splitRequest[2]*4+2, 4):    #verifica de filename em filename
                if (splitRequest[i] != listaDoBS[i-1] or splitRequest[i+1] != listaDoBS[i] or splitRequest[i+2] != listaDoBS[i+1] or splitRequest[i+3] != listaDoBS[i+2]):
                    returnList += splitRequest[i] + splitRequest[i+1]+splitRequest[i+2]+splitRequest[i+3]
            return 'BKR '+ ??IPBS?? + ??portBS?? + splitRequest[2] + returnList + '\n'

    elif (msgCode == 'RST'):
        try:
            #caso em que o dir existe e por isso tem um BS associado
            if len(os.listdir('/CS/user_' + user)) != 0:
                f = open('/CS/user_' + user + '/' + splitRequest[1] + '/IP_port.txt', 'r')
                info = f.readlines()        #o info vai ser algo assim: ['adfsafd', 'sdfgsdg']
                return 'RSR ' + info[0] + ' ' + info[1] + '\n'
            else:
                return 'RSR EOF\n'
        except:
            return 'RSR ERR\n'

    elif (msgCode == 'LSD'):
        reply = ''
        n = 0
        for dir in os.listdir('/CS/user_' + user):
            reply += ' ' + dir
            n += 1
        return 'LDR ' + n + reply + '\n'

    elif (msgCode == 'LSF'):
        try:
            serverUDP.sendto('LSF ' + user + splitRequest[1], SERVER_SOCKET)
            # recebe 'LFD' por udp do bs
            ###   TODO   ###

            return 'LFD ' + BSip + ' ' + BSport + ??resposta??[3:] +'\n'   #resposta do BS
        except:
            return 'LFD NOK\n'

    elif (msgCode == 'DEL'):
        serverUDP.sendto('DLB ' + user + splitRequest[1], SERVER_SOCKET)
        # recebe 'DBR' por udp do bs
        ###   TODO    ###
        splitMessage = message.split(' ')
        if (splitMessage[1] == 'OK\n'):
            shutil.rmtree('/CS/user_'+ user + '/' + splitRequest[1])  #remove a dir do user
            return 'DDR OK\n'
        else:
            return 'DDR NOK\n'
    else:
        return 'ERR\n'

def dealWithBS(data):
    splitData = data.split(' ')
    msgCode = splitData[0]
    if (msgCode == 'REG'):  # quando e que deve declinar??
        try:
            if (splitData[1] in dataBS):
                print ('O BS ja esta registado')
                return 'RGR NOK\n'
            else:
                dataBS[splitData[1]] = splitData[2]  # guarda se o ipBS e o portBS num dicionario
            return 'RGR OK\n'
        except:
            return 'RGR ERR\n'

    elif (msgCode == 'UNR'):  # quando e que deve declinar?
        try:
            if (splitData[1] in dataBS):
                del dataBS[splitData[1]]
                return 'UAR OK\n'
            else:
                return 'UAR NOK\n'
        except:
            return 'UAR ERR\n'


def TCPconnection():
    '''Precisamos do select para nao bloquear no serverTCP.accept()'''
    connection, addrTCP = serverTCP.accept()  # Assign here, if it didn't raise error.
    print 'connection address: ', addrTCP
    request = connection.recv(BUFFER_SIZE)
    print 'request: ', request
    answerUser = dealWithUser(request)
    connection.send(answerUser)
    connection.close()

def UDPconnection():
    data, addrUDP = serverUDP.recvfrom(BUFFER_SIZE)
    print 'connection asdress: ' + addrUDP
    print 'request: ', data
    answerBS = dealWithBS(data)
    serverUDP.sendto(answerBS, SERVER_SOCKET)
    #connection.close()     ???


###### MAIN #######

SERVER_SOCKET = ( socket.gethostbyname(CS_IP), int( CS_PORT ) )

######  TCP CONECTION   #######
serverTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverTCP.bind(SERVER_SOCKET)
serverTCP.listen(5)

#####       UDP connection       ######
serverUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverUDP.bind(SERVER_SOCKET)


input = [serverTCP, serverUDP]		#Os respetivos sockets

while True:
#The select() function will block until one of the socket states has changed.

    print("Cheguei ao select\n")
    inputready, outputready, exceptready = select(input,[],[])
    print("Selecionei canal do select\n")
    for s in inputready:
	    if s == serverTCP:
			TCPconnection()
		elif s == serverUDP:
			UDPconnection()
		else:
			print "unknown socket:", s


