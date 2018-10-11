import socket
import os
import shutil
import select
from multiprocessing import Lock, Process

CS_IP = socket.gethostbyname(socket.gethostname())
CS_PORT = 58001

BUFFER_SIZE = 1024
MESSAGE = "Server accepted connection"

# last login data
user = ''
password = ''

dataBS = {}
returnList = []

print CS_IP
print 'running'

def dealWithUser(request):
    splitRequest = request.split(' ')
    msgCode = splitRequest[0]  # AUT / DLU / DLR etc...
    print "start dealWithUser"
    if (msgCode == 'AUT'):
    	print 'user:', splitRequest[1]
    	if(os.path.isfile('user_'+splitRequest[1]+'.txt')):
    		f = open('user_' + splitRequest[1]+ '.txt', "r")
    		uPass = f.read()  # fica com a pass do user
    		if (uPass == splitRequest[2]):
    			user = splitRequest[1]  # guardar o ultimo login
    			password = splitRequest[2]
    			status = 'OK'
    		else:
    			status = 'NOK'
        else:  # User novo. Para cada user criado, e tbm criado uma diretoria para o user
            user = splitRequest[1]  # guardar o ultimo login
            password = splitRequest[2]
            f = open('user_' + user + '.txt', 'w')  # cria o fich do user e vai escrever a pass
            f.write(password)
            os.makedirs(os.path.expanduser('./user_' + user))  # cria o dir do user
            status = 'NEW'
        return 'AUR ' + status + '\n' # return answer to user

    elif (msgCode == 'DLU'):    #para haver info guardada e preciso haver uma dir do user
    	print 'entrou DLU'
        if len(os.listdir('./user_'+user)) == 0:  #verificar se a dir do user esta vazia
            status = 'OK'
            os.remove('./user_' + user + '.txt')  #remover o fich user e a sua dir
            os.remove('./user_' + user)
        else:
            status = 'NOK'
       	print status
       	return 'DLR ' + status + '\n'

    elif (msgCode == 'LSD'):
    	reply = ''
    	n = 0
    	for dirc in os.listdir('./user_' + user):
    		reply += ' ' + dirc
    		n += 1
    		return 'LDR ' + n + reply + '\n'



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


def TCPconnection(serverTCP):
	while  True:
		connection, addrTCP = serverTCP.accept()  # Assign here, if it didn't raise error.
		print 'connection address: ', addrTCP
		request = connection.recv(BUFFER_SIZE)
		print 'request: ', request
		answerUser = dealWithUser(request)
		connection.send(answerUser)
		connection.close()

def UDPconnection(SERVER_SOCKET):
	print SERVER_SOCKET
	data, addrUDP = serverUDP.recvfrom(BUFFER_SIZE)
	print 'connection address: ' + str(addrUDP)
	print 'request: ', data.decode()
	answerBS = dealWithBS(data.decode())
	print answerBS
	serverUDP.sendto(answerBS.encode(), SERVER_SOCKET)
	print "yo"
	serverUDP.close()


###### MAIN #######

SERVER_SOCKET = ( CS_IP, int( CS_PORT ) )

######  TCP CONECTION   #######
serverTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverTCP.bind(SERVER_SOCKET)
serverTCP.listen(5)

process_user = Process(target=TCPconnection, args=(serverTCP,))  
process_user.daemon = True
process_user.start()

while 1:
	#####       UDP connection       ######
	serverUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serverUDP.bind(SERVER_SOCKET)
	UDPconnection(SERVER_SOCKET)
	# process_backup = Process(target=UDPconnection, args=(SERVER_SOCKET,))
	# process_backup.start()
