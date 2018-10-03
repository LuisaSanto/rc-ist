import socket
import argparse

CS_IP = socket.gethostbyname("tejo.ist.utl.pt")
#IP EXTERNAL NETWORK 193.136.138.142
#IP INTERNAL NETWORK 192.168.1.2
CS_PORT = 58011
BS_IP = None
BS_PORT = None
BUFFER_SIZE = 1024
MESSAGE = "user connected?"
digits = ['0','1','2','3','4','5','6','7','8','9']
passCode = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
input_flag = 1

user = None
passeword = None
aurState = ''

print "IP:", CS_IP
print "PORT:", CS_PORT
#s.connect((CS_IP, CS_PORT))
#s.send(MESSAGE)
#response = s.recv(BUFFER_SIZE)
#s.close()

def login(user, passe):
	#if (user.isdigit() ):#&& add way to parse 'passe' ): check split()
		#TO_DO
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((CS_IP, CS_PORT))
	s.send('AUT ' + user +' '+ passe +'\n')
	global aurState
	aurState = s.recv(BUFFER_SIZE)
	print aurState
	s.shutdown(socket.SHUT_RDWR)
	s.close()

def deluser():
	#TO_DO
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((CS_IP, CS_PORT))
	s.send('DLU\n')
	response = s.recv(BUFFER_SIZE)
	print "response:", response
	s.shutdown(socket.SHUT_RDWR)
	s.close()
	#add way to check if login was done
	#add way to check if there is no information (this should be done in the CS, the user just waits)
	#wait for CS to confirm

def dirlist():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((CS_IP, CS_PORT))
	s.send('LSD') #how to send the list of files in direc
	response = s.recv(BUFFER_SIZE)
	response2 = s.recv(BUFFER_SIZE)
	print response
	print response2
	#ver o que se passa com o wireshark

#######################################
#----------------MAIN-----------------#
#######################################
print '***************\nCommands:\n  login *user* *password*\n  dirlist\n***************\n'
while True:	
	inpt = raw_input("pls input")
	inpt.split(" ")
	num_of_spaces = inpt.count(' ')
	processed_input = inpt.split(' ')
	if num_of_spaces == 0:
		if(processed_input[0]== 'dirlist'):
			print 'entrou'
			print aurState
			if(aurState == 'AUR OK\n'):
				
				dirlist()
			if(aurState == 'AUR NEW\n'):
				login(user,passeword)
				dirlist()
			#if(aurState == 'ERR')
	if num_of_spaces == 1:
		pass #TO_DO
	if num_of_spaces == 2:
		if(processed_input[0]== 'login'):
			if (len(processed_input[1]) == 5 and len(processed_input[2]) == 8):
				for i in processed_input[1]:
					if(i not in digits):
						input_flag = 0
						break
				for j in processed_input[2]:
					if(j not in passCode and j not in digits):
						input_flag = 0
						break
				if(input_flag == 1):
					user = processed_input[1]
					passeword = processed_input[2]
					login(user, passeword)
					input_flag = 1
#deluser() #nao funciona no CS do tejo


def backup(direc):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((CS_IP, CS_PORT))
	s.send(direc) #how to send the list of files in direc
	response = s.recv(BUFFER_SIZE)
	print "response:", response
	s.close()
	#arranjar maneira de dividir o que receber BS_IP BS_PORT
	b = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	b.connect(BS_IP, BS_PORT)
	#b.send(STUFF)
	response = b.recv(BUFFER_SIZE)
	print "response:", response
	b.close()

#def restore(dir):
	#TO_DO

#def filelist(dir):
	#TO_DO

#def delete(dir):
	#TO_DO

#def logout():
#TO_DO