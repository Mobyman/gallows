import socket, string, threading, sys
global HOST, PORT

print "Hello!\n"

HOST = getfqdn(gethostname())
PORT = 14880
fullServerFlag = False

class Server:
  
  def listen():
    
    try:
      server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      server.bind((HOST, PORT))
      server.listen(1)
      
    except socket.error, detail: print detail
      
    while (fullServerFlag != True):
      users = [server.fileno()]  
      conn, addr = server.accept()
      try: iw, ow, er = select.select(users, [], [], 3)
      except: print detail
      
      print "%s has been connected!" % addr
        
    conn.close()

