import socket, string, threading, sys
global HOST, PORT

print "Hello!\n"

HOST = getfqdn(gethostname())
PORT = 14880

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(HOST, PORT)
server.listen(1)


