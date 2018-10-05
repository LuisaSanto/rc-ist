import socket

CS_IP = 192.168.1.2#insert central server IP
CS_PORT = 58011#insert
BUFFER_SIZE = 256
MESSAGE = "Server accepted connection"

#last login data
user = None
password = None

######  TCP CONECTION   #######
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((CS_IP,CS_PORT))
s.listen(1)
connection, addr = s.accept()

print 'connection address:', addr

while  1:
	request = connection.recv(BUFFER_SIZE)
    dealWithUser(connection, request, BUFFER_SIZE)
	if not response: break
	print "response recived", response



def dealWithUser(user_socket, request, BUFFER_SIZE):
	answerUser = userRequestTPC(user_socket, request, BUFFER_SIZE)
    user_socket.send(answerUser)
	user_socket.close()



def userRequestTCP(socket, request, BUFFER_SIZE):
    splitRequest = request.split()
    msgCode = splitRequest[0]       #AUT / DLU / DLR etc...
    if (msgCode == 'AUT'):
        if (///find matching user///):
            if(///password s right///):
                status = 'OK'
            else:
                status = 'NOK'
        else:
            ///save new user & password///
            status = 'NEW'
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
        ///TO_DO///
        return 'BKR' +

    elif (msgCode == 'RST'):
        ///TO_DO///
        return 'RSR' +

    elif (msgCode == 'LSD'):
        ///TO_DO///
        return 'LDR' +

    elif (msgCode == 'LSF'):
        ///TO_DO///
        return 'LSD' +







