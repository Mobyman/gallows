from socket import * 
from string import *
from sys import exit
from threading import * 
from select import select 
from time import *
from random import randrange
import socket, string, sys, threading, select, time

global HOST, PORT, LOG, usersword
HOST, PORT = "", 6000

LOG = "server_log.txt"

def logging(text):
  logg = open(LOG, "a+")
  logg.write(asctime() + ": " + text + "\n")
  logg.close()
  print text + "\n"

def sendmsg(msg, adr):
  for sock in users.keys():
    sock.send(msg)

class Gallows:
  def generate(self):
    wordsfile = open('words.txt', 'r')
    words = wordsfile.readlines()
    length = len(words)
    wordindex = randrange(0, length)
    wordsfile.close()
    self.secret = strip(words[wordindex])
    return self.secret
  
  def getletter(self, uword, letter):
    iter1 = True # Edit strings %)
    for x in range(len(self.secret)):
      if (self.secret.find(letter) != -1):
          pos = self.secret.find(letter)
          tmp = self.secret
          tmp = tmp[:pos] + letter + tmp[pos+1:]
          if (iter1):
            newuword = uword[:pos] + letter + uword[pos+1:]
          else:
            newuword = uword[:pos] + letter + uword[pos+1:]
      iter1 = False

    guessed = self.secret.count(letter)
    print "Letter %s\n" % letter
    if newuword.count("*") == -1:
      guessed = -1
    return [guessed, newuword]
  
class Server:
    # listen for connections 
    class Listen_for_connections(Thread):
        def __init__(self):
            Thread.__init__(self)
            
        def run(self):
            global users, server, rl, sockets
            try:
                server = socket.socket(AF_INET, SOCK_STREAM)
                server.bind((HOST, PORT))
                server.listen(1)
            except socket.error, detail:
                print detail
            username = "\nPrisoner"
            usercount = 0 
            users = {}
            attempt = 10
            sockets = [""]
            while 1:
                if sockets[-1] == "CLOSED":
                    break
                sockets = [server.fileno()]
                for sock in users.keys():
                    sockets.append(sock.fileno())
                try:
                    rl, wl, el = select.select( sockets, [], [], 3)
                except select.error, detail:
                    print detail
                    break
                for n in rl:
                    if n == server.fileno():
                        sock, addr = server.accept()
                        users[sock] = username + str(usercount)
                        usercount += 1
                        #if (usercount > 1):
                        gallows = Gallows()
                        word = gallows.generate()
                        usersword = word[0] + "*" * (len(word) - 2) + word[-1] 
                        print "Secret word generated! [%s]. \nFor users: %s" % (word, usersword)
                        sendmsg("Secret word generated! [%s]." % str(usersword), sock)
                          
                    else:
                        for sock in users.keys():
                            if sock.fileno() == n: break
                        name = users[sock]
                        try:
                            text = sock.recv(1024)
                        except socket.error, detail:
                            print detail
                            break
                        if not text:
                            sendmsg("%s has been disconnected!" % name, sock)
                            logging(name+" has been disconnected!")
                            sleep(1)
                            userscount -= 1
                            # close the socket
                            sock.close()
                            # delete user from list
                            del users[sock]
                        else:
                            try:
                              a = """if (text[:6] == "!char "):
                                letter = strip(text[6:])
                                if (len(text) > 1):
                                  sock.close()
                                  logging("Member %s kicked!") % name
                                else: """
                              result = []
                              guessed = 0
                              result = gallows.getletter(usersword, strip(text))
                              usersword = result[1]
                              if (result[0] != 0):
                                if (result[0] > 0):
                                  sendmsg("Congratulations, %s you've guessed the letter [%s]!" % (name, usersword), sock)
                                elif (result[0] == -1):
                                  sendmsg("Congratulations, %s you've guessed the word [%s]!" % (name, usersword), sock)
                                  
                              else:
                                sendmsg("%s, try another letter:( [%s] %d" % (name, usersword, result[0]), sock)
                                attempt -= 1
                                
                            except socket.error, detail:
                                print detail
                                break
                            logging(str(name)+": "+text)
    lc=Listen_for_connections()
    

def disconnect():
  global getout
  for sock in users.keys():
    try:
      sock.send("server closed the connection")
    except error, detail:
      print detail
    sock.close()
    del users[sock]
  sleep(1)
  # logging
  if LOGGING == "ON":
    logging("server closed the connection\n")
  print "server closed"
  # close the mainserver
  server.close()
  sockets.append("CLOSED")

# make a server instance
s=Server()

# START the server
def start():
  s.lc.start()

