
import socket
import argparse

CS_IP = #insert central server IP
CS_PORT = #insert
BUFFER_SIZE = 256
MESSAGE = "user connected?"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((CS_IP, CS_PORT))
s.send(MESSAGE)
response = s.recv(BUFFER_SIZE)
s.close()

print "response:", response

def login(user, passe):
	if (user.isdigit() ):#&& add way to parse 'passe' ):
		#TO_DO
		s.connect((CS_IP, CS_PORT))
		s.send('AUT ' + user +' '+ passe)


def deluser():
	#TO_DO
	#add way to check if login was done
	#add way to check if there is no information (this should be done in the CS, the user just waits)
	#wait for CS to confirm

def backup(dir):
	#TO_DO

def restore(dir):
	#TO_DO

def dirlist():
	#TO_DO

def filelist(dir):
	#TO_DO

def delete(dir):
	#TO_DO

def logout():
	#TO_DO