import socket
import sys
import os
import time

reload(sys)  
sys.setdefaultencoding('utf8')

CS_IP = '127.0.1.1'
#CS_IP = socket.gethostbyname("tejo.ist.utl.pt")
#IP EXTERNAL NETWORK 193.136.138.142
#IP INTERNAL NETWORK 192.168.1.2
CS_PORT = 58001
BS_IP = None
BS_PORT = None
BUFFER_SIZE = 1024
MESSAGE = "user connected?"
digits = ['0','1','2','3','4','5','6','7','8','9']
passCode = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
input_flag = 1

s = None

user = None
password = None
aurState = ''

loginflag = 0 #if == 0: no login done, aka no TCP connection open

print "IP:", CS_IP
print "PORT:", CS_PORT
#s.connect((CS_IP, CS_PORT))
#s.send(MESSAGE)
#response = s.recv(BUFFER_SIZE)
#s.close()

def login(uzer, passe):
	#TO_DO?
	global s
	global loginflag
	global aurState
	if(loginflag==0 and ((user == None and password == None) or (user == uzer and password == passe))):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((CS_IP, CS_PORT))
		s.send('AUT ' + uzer +' '+ passe +'\n'.encode())
		aurState = s.recv(BUFFER_SIZE).decode()
		print aurState
		loginflag = 1
		return 1
	else:
		print "login already done OR current user must logout before a new one log's in"
		return 0

def deluser():
	#TO_DO?
	global s
	global loginflag
	if (loginflag == 0):
		login(user, password)
	s.send('DLU\n'.encode())
	response = s.recv(BUFFER_SIZE).decode()
	print response
	#s.shutdown(socket.SHUT_RDWR)
	s.close()

	loginflag = 0
	#add way to check if login was done
	#add way to check if there is no information (this should be done in the CS, the user just waits)
	#wait for CS to confirm

def dirlist():
	global s
	global loginflag
	if (loginflag == 0):
		login(user, password)
	s.send('LSD\n'.encode()) #how to send the list of files in direc
	c = ""
	content = ""
	while c!="\n" :
		c = s.recv(1).decode()
		content+=c
	print content
	s.shutdown(socket.SHUT_RDWR)
	s.close()
	loginflag = 0
	

def backup(direc):
	#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#s.connect((CS_IP, CS_PORT))
	global loginflag
	if (loginflag == 0):
		login(user, password)
	fileslist = os.listdir(direc)
	n = 0
	msg = ''
	final = "BCK " + direc
	for file in fileslist:
		msg += ' ' + file
		msg += ' ' + time.strftime('%d.%m.%Y %H:%M:%S', time.gmtime(os.path.getmtime(direc+"/"+file)))
		msg += ' ' + str(os.path.getsize(direc+"/"+file))
		n += 1
	final += ' ' + str(n) + msg + '\n'
	print final
	try:
		#sends directory name and file details to CS
		s.send(final.encode())
	except socket.error as err:
		print("This is an error from send fun {}".format(err))
	
	try:
		c = ""
		response = ""
		while c != '\n':
			#NO DECODE
			c = s.recv(1)
			response += c
	except socket.error as err:
		print("This is an error from recive fun {}".format(err))

	print response
	print '+++++++++'
	s.close()
	splitresponse = response.split()

	

	if (splitresponse[0]== 'BKR'):
		if(splitresponse[1] != 'EOF' and splitresponse[1]!='ERR'):
			BS_IP = splitresponse[1]
			BS_PORT = splitresponse[2]

			n = int(splitresponse[3])
			i = 0

			finalstring = 'UPL '+ direc + ' ' + str(n).encode()
			while n != 0:
				filename = splitresponse[i+4]
				filedate = splitresponse[i+5]
				filetime = splitresponse[i+6]
				filesize = splitresponse[i+7]
				finalstring +=' '+filename+' '+filedate+' '+filetime+' '+filesize+' '.encode()

				file = open(direc +'/'+ filename, 'rb')
				filecontent = file.read()
				filecontent = filecontent.encode()
				file.close()
				finalstring += filecontent

				i += 4
				n -= 1

			b = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			b.connect((BS_IP, eval(BS_PORT)))
			print (BS_IP,BS_PORT)
			b.send('AUT ' + user +' '+ password +'\n')
			r = b.recv(BUFFER_SIZE)
			print (user,password)
			print r
			#if(r == 'AUR OK'):
			print '--------'
			finalstring += '\n'
			print finalstring
			b.send(finalstring)
			try:
				response = b.recv(BUFFER_SIZE).decode()
			except socket.error as err:
				print("This is an error from send fun {}".format(err))
			print'~~~~~~'
			print response
			b.close()
		loginflag = 0

def filelist(dirc):
	global s
	global loginflag
	if (loginflag == 0):
		print (user, password)
		login(user, password)
	s.send("LSF "+ dirc +"\n".encode())
	c = ""
	content = ""
	while c!="\n" :
		c = s.recv(1).decode()
		content+=c

	print content
	s.shutdown(socket.SHUT_RDWR)
	s.close()
	loginflag = 0

def delete(dirc):
	global s
	global loginflag
	if (loginflag == 0):
		print (user, password)
		login(user, password)
	s.send("DEL "+ dirc +"\n".encode())
	response = s.recv(BUFFER_SIZE).decode()
	print response
	loginflag = 0

def restore(dirc):
	global s
	global BS_IP
	global BS_PORT
	global loginflag
	if (loginflag == 0):
		print (user, password)
		login(user, password)
	s.send("RST "+ dirc +"\n".encode())
	response = s.recv().decode()
	print response
	r1 = response.split(" ")
	if(r1[0] == 'RSR'):
		BS_IP = r1[1]
		BS_PORT = r1[2]
		b = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		b.connect((BS_IP, BS_PORT))
		b.send('RSB '+ direc + '\n'.encode())
		response = b.recv(BUFFER_SIZE)
		r2 = response.split(' ')
		if(r2[0] == 'RBR'):
			n = r2[1]
			while n != 0:
				filename = r2[i+2]
				filedate = r2[i+3]
				filetime = r2[i+4]
				filedata = r2[i+5]
				i += 4
				n -= 1


def logout():
	global user
	global password
	global loginflag
	if (loginflag == 1):
		s.close()
		loginflag = 0
		print user + " logged out"
	else:
		print "no login was done OR TCP connection already closed"
	user = None
	password = None

def exit():
	global loginflag
	if(loginflag == 1):
		logout()
	sys.exit()
#######################################
#----------------MAIN-----------------#
#######################################
print '***************\nCommands:\n  login *user* *password*\n  dirlist\n***************\n'
while True:	
	inpt = raw_input("~")
	inpt.split(" ")
	num_of_spaces = inpt.count(' ')
	processed_input = inpt.split(' ')
	if num_of_spaces == 0:
		#---------------DELUSER--------------#
		if(processed_input[0]== 'deluser'):
			if(aurState == 'AUR OK\n'):
				deluser()
			if(aurState == 'AUR NEW\n'):
				login(user,password)
				deluser()
		#---------------DIRLIST--------------#
		if(processed_input[0]== 'dirlist'):
			if(aurState == 'AUR OK\n'):
				dirlist()
			if(aurState == 'AUR NEW\n'):
				login(user,password)
				dirlist()
			#if(aurState == 'ERR')
		#--------------LOGOUT----------------#
		if(processed_input[0]== 'logout'):
			logout()
		#---------------EXIT-----------------#
		if(processed_input[0]== 'exit'):
			exit()

	if num_of_spaces == 1:
		#-------------FILELIST---------------#
		if(processed_input[0]== 'filelist'):
			print processed_input[1]
			if(aurState == 'AUR OK\n'):
				filelist(processed_input[1])
			if(aurState == 'AUR NEW\n'):
				login(user,password)
				filelist(processed_input[1])

		#---------------BACKUP---------------#
		if(processed_input[0]== 'backup'):
			if(aurState == 'AUR OK\n'):
				backup(processed_input[1])
			if(aurState == 'AUR NEW\n'):
				login(user,password)
				backup(processed_input[1])

		if(processed_input[0]== 'delete'):
			print processed_input[1]
			if(aurState == 'AUR OK\n'):
				delete(processed_input[1])
			if(aurState == 'AUR NEW\n'):
				login(user,password)
				delete(processed_input[1])

	if num_of_spaces == 2:
		#---------------LOGIN---------------#
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
					if (login(processed_input[1], processed_input[2])):
						user = processed_input[1]
						password = processed_input[2]
input_flag = 1