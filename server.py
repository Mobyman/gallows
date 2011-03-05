# -*- coding: utf-8 -*-
import socket, string, threading, sys, select
global HOST, PORT



class Server:
  

    
  def run(self):

    uobj = [] 
    uready = []
    running = 1
    gamers = {} # addr, attempt
     
    while running:
      nusers = [self.server]  
      try: iw, ow, ew = select.select(nusers, [], [])
      except select: print "Error select"
      
      for num in iw:
        if num == self.server():
          conn, addr = self.server.accept()
          #self.newconn(str(num))
          gamers[conn] = {addr, 10}
          buf = num.recv(1024)
          print buf
          break
        else:
          data = num.recv(1024)
          if data:
            print data
            #conn.close()
          else:
            break
          

  def __init__(self):
    print "Hello!\n"
    HOST = "localhost" #gethostbyaddr(gethostname())
    PORT = 14880
    try:
      self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.server.bind((HOST, PORT))
      self.server.listen(1)
    except socket.error, detail: print detail
    self.run()
    
  def newconn(self, user):
    print "%s has been connected!" % user
    # Добавить!

server = Server()

              