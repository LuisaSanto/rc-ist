import socket

CS_IP = 192.168.1.2#insert central server IP
CS_PORT = 58011#insert
BUFFER_SIZE = 256
MESSAGE = "Server accepted connection"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((CS_IP,CS_PORT))
s.listen(1)

connection, addr = s.accept()
print 'connection address:', addr
while  1:bind
	response = connection.recv(BUFFER_SIZE)
	if not response: break
	print "response recived", response
	connection.send(MESSAGE)
connection.close() 