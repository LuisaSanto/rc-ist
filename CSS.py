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
loginFlag = 0

print CS_IP
print 'running'

def dealWithUser(request):
	global loginFlag
	global user
	global password
	splitRequest = request.split(' ')
	msgCode = splitRequest[0]  # AUT / DLU / DLR etc...
	print "start dealWithUser: " + msgCode
	if (msgCode == 'AUT'):
		print 'user:', splitRequest[1]
		if(os.path.isfile('user_'+splitRequest[1]+'.txt')):
			f = open('user_' + splitRequest[1]+ '.txt', "r")
			uPass = f.read()  # fica com a pass do user
			if (uPass == splitRequest[2]):
				user = splitRequest[1]  # guardar o ultimo login
				password = splitRequest[2]
				status = 'OK'
				loginFlag = 1
			else:
				status = 'NOK'
		else:  # User novo. Para cada user criado, e tbm criado uma diretoria para o user
			user = splitRequest[1]  # guardar o ultimo login
			password = splitRequest[2]
			f = open('user_' + user + '.txt', 'w')  # cria o fich do user e vai escrever a pass
			f.write(password)
			os.makedirs(os.path.expanduser('./user_' + user))  # cria o dir do user
			status = 'NEW'
			loginFlag = 1
		return 'AUR ' + status + '\n' # return answer to user

	elif (msgCode == 'DLU\n'):    #para haver info guardada e preciso haver uma dir do user
		global loginFlag 
		global user
		print 'entrou DLU'
		if len(os.listdir('./user_'+user)) == 0:  #verificar se a dir do user esta vazia
			status = 'OK'
			os.remove('./user_' + user + '.txt')  #remover o fich user e a sua dir
			os.rmdir('./user_' + user)
		else:
			status = 'NOK'
		print status
		loginFlag = 0
		return 'DLR ' + status + '\n'

	elif (msgCode == 'LSD\n'):
		global loginFlag
		global user
		print 'entrou LSD'
		reply = ''
		n = 0
		for dirc in os.listdir('./user_' + user):
			reply += ' ' + dirc
			n += 1
		loginFlag = 0
		return 'LDR ' + str(n) + reply + '\n'

	elif (msgCode == 'RST'):
		global loginFlag
		global user
		print 'entrou RST'
		try:
			f = open('./user_' + user + '/' + splitRequest[1][:-1] + '/IP_port.txt', 'r') 	#splitRequest[1] = 'Dir\n'
			bsInfo = f.readlines()       
			print bsInfo 
			a = ''.join(bsInfo)
			info = a.split(' ')
			loginFlag = 0
			return 'RSR ' + info[0] + ' ' + info[1] + '\n'
		except:
			return 'RSR EOF\n'

	#DAQUI PARA CIMA TUDO A FUNCIONAR

	elif (msgCode == 'DEL'):
		serverUDP.sendto('DLB ' + user + splitRequest[1], SERVER_SOCKET)    #UDP enviar e receber do BS
		time.sleep(3)
		resposta, addrUDP = serverUDP.recvfrom(BUFFER_SIZE)
		splitResposta = resposta.split(' ')
		if (splitResposta[1] == 'OK\n'):
			shutil.rmtree('./user_'+ user + '/' + splitRequest[1])  #remove a dir do user
			return 'DDR OK\n'
		else:
			return 'DDR NOK\n'	

	elif (msgCode == 'LSF'):
		global loginFlag
		global user
		try:
			serverUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			serverUDP.bind(SERVER_SOCKET)
			serverUDP.sendto('LSF ' + user + splitRequest[1], SERVER_SOCKET)  #UDP enviar e receber do BS
			print 'MENSAGEM ENVIADA'
			time.sleep(3)
			resposta, addrUDP = serverUDP.recvfrom(BUFFER_SIZE)
			return 'LFD ' + BSip + ' ' + BSport + resposta[3:] +'\n'   #resposta do BS
		except:
			return 'LFD NOK\n'

	elif (msgCode == 'BCK'):
		global loginFlag
		global user
		global password
        #estou a supor que para cada user, cada dir e guardada por um bs unico
        #verificar se o user ja tem info no BS -> precisa de ter uma dir com o ip do BS
        if os.path.isdir("./user_" + user + '/' + splitRequest[1]) == True:
            #ja existe uma dir com um backup
            serverUDP.sendto('LSF ' + user + ' ' + splitRequest[1], SERVER_SOCKET)
            time.sleep(3)
            resposta, addrUDP = serverUDP.recvfrom(BUFFER_SIZE)
            splitResposta = resposta.split(' ')
            for i in range(3, splitRequest[2]*4+2, 4):    #verifica de filename em filename
                if (splitRequest[i] != splitResposta[i-1] or splitRequest[i+1] != splitResposta[i] or splitRequest[i+2] != splitResposta[i+1] or splitRequest[i+3] != splitResposta[i+2]):
                    returnList += splitRequest[i] + splitRequest[i+1]+splitRequest[i+2]+splitRequest[i+3]
            return 'BKR '+ str(addrUDP[0]) + str(addrUDP[1]) + splitRequest[2] + returnList + '\n'
        else:
            # user novo por isso cria se dir no CS e um fich com os dados do BS
            serverUDP.sendto('LSU ' + user + ' ' + password, SERVER_SOCKET)  #registar user no BS
            #recebe 'LUR status' do BS
            time.sleep(3)
            resposta, addrUDP = serverUDP.recvfrom(BUFFER_SIZE)
            splitResposta = resposta.split(' ')
            if splitResposta[1] == 'OK':
                os.makedirs(os.path.expanduser('./user_' + user + '/' + splitRequest[1]))
                f = open('./user_' + user + '/' + splitRequest[1] + '/IP_port.txt', 'w')
                f.write(str(addrUDP[0]) + ' ' + str(addrUDP[1]))
                return 'BKR' + str(addrUDP[0]) + str(addrUDP[1]) + ' '.join(splitRequest[2:]) + '\n'
            else:
                print('O LSU falhou porque a resposta foi: ' + resposta)
                return 'BKR EOF\n'

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
	global login
	while  True:
		print 'waiting...'
		if loginFlag != 1:
			connection, addrTCP = serverTCP.accept()  # Assign here, if it didn't raise error.
			print 'connection address: ', addrTCP
		request = connection.recv(BUFFER_SIZE)
		print 'request: ', request
		answerUser = dealWithUser(request)
		connection.send(answerUser)
		print 'loginFlag: ', loginFlag
		if loginFlag != 1:
			connection.close()

def UDPconnection(SERVER_SOCKET):
	print SERVER_SOCKET
	data, addrUDP = serverUDP.recvfrom(BUFFER_SIZE)
	print 'connection address: ' + str(addrUDP)
	print 'request: ', data
	answerBS = dealWithBS(data)
	print 'answer: ', answerBS	
	serverUDP.sendto(answerBS, addrUDP)
	#serverUDP.close()

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

