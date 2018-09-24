
import socket

#creates an INET, STREAMing socket and binds it
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cs_ip = gethostbyname("guadiana")
print "cs_ip: ",cs_ip

server_socket.bind(cs_ip)

while 1:
	second_soket.accept()
	print "second_soket.adrs", second_soket[1]

	second_soket.close()

server_socket.close()


