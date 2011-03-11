#-*- coding:utf-8 -*-
"""
@license: GNU GPL v2
@author: Egorov Ilya
@version: 0.7
"""
from socket import * 
from string import *
from sys import exit
from threading import * 
from select import select 
from time import *
from random import randrange
import socket, string, sys, threading, select, time, logging

global HOST, PORT, LOG, usersword, ATTEMPT_MAX, USERNAME, gallows
HOST, PORT = "", 6000
ATTEMPT_MAX = 10
USERNAME = "Prisoner"
logger = logging.getLogger("server")
logger.setLevel(logging.DEBUG)
logstream = logging.StreamHandler()
logstream.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:  %(message)s")
logstream.setFormatter(formatter)
logger.addHandler(logstream)

def sendmsg(msg, adr):
  for sock in users.keys():
    sock.send(msg)

def clean():
  usercount = 0 
  users = {}
  sockets = [""]
  gallows.attempts = ATTEMPT_MAX

  
class Gallows:
   
  def __init__(self):
    self.attempts = ATTEMPT_MAX
  """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" 
  @return: слово, сгенерированное из словаря
  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""   
  def generate(self):
    wordsfile = open('words.txt', 'r')
    words = wordsfile.readlines()
    length = len(words)
    wordindex = randrange(0, length)
    wordsfile.close()
    self.secret = strip(words[wordindex])
    return self.secret
  
  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  @param:
    uword: слово, видимое игрокам
    letter: буква, предложенная пользователем
  @return:
    guessed: количество верно угаданных букв (если -1, то угадано слово)
    newuword: слово, видимое игрокам, с учетом параметра letter
  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  def getletter(self, uword, letter):
    if (uword.count(letter)>0):
      logger.info("Letter already opened")
      guessed = -2
      newuword = uword
    else:  
      iter1 = True # Edit strings %)
      guessed = self.secret.count(letter)
      tmp2 = uword
      for x in range(len(self.secret)):
        if (self.secret.find(letter) != -1):
            pos = self.secret.find(letter)
            tmp = self.secret
            logger.debug("Position:" + str(pos))
            self.secret = tmp[:pos] + "@" + tmp[pos+1:]
            if (iter1):
              tmp2 = uword[:pos] + letter + uword[pos+1:]
            else:
              tmp2 = tmp2[:pos] + letter + tmp2[pos+1:]
        iter1 = False
      logger.info("Letter %s; Attempts: %d" % (letter, self. attempts))
      if tmp2.count("*") == 0:
        guessed = -1
      newuword = tmp2
    return [guessed, newuword]

  
class Server:
    # listen for connections 
    class Listen_for_connections(Thread):
        def __init__(self):
            Thread.__init__(self)
            
        def run(self):
            global users, server, rl, sockets, usercount, gallows
            gallows = Gallows()
            try:
                server = socket.socket(AF_INET, SOCK_STREAM)
                server.bind((HOST, PORT))
                logger.debug("Server binded")
                server.listen(1)
                logger.debug("Server listen")
            except socket.error, detail:
                logger.error(detail)
            USERNAME = "Prisoner"
            usercount = 0 
            users = {}
            sockets = [""]
            while 1:
                if sockets[-1] == "CLOSED":
                    break
                sockets = [server.fileno()]
                for sock in users.keys():
                    sockets.append(sock.fileno())
                try:
                    rl, wl, el = select.select(sockets, [], [], 3)
                except select.error, detail:
                    logger.error(detail)
                    break
                for n in rl:
                    if n == server.fileno():
                        sock, addr = server.accept()
                        logger.info("New user #" + str(n))
                        users[sock] = USERNAME + str(usercount)
                        usercount += 1
                        #if (usercount > 1):
                        restart = True
                          
                    else:
                        for sock in users.keys():
                            if sock.fileno() == n: break
                        name = users[sock]
                        try:
                            text = sock.recv(1024)
                        except socket.error, detail:
                            logger.error(detail)
                            break
                        if not text:
                            sendmsg("%s has been disconnected!" % name, sock)
                            logger.info(name+" has been disconnected!")
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
                                  logger.info("Member %s kicked!") % name
                                else: """
                              result = []
                              guessed = 0
                              letter = strip(text)
                              result = gallows.getletter(usersword, letter)
                              usersword = result[1]
                              restart = False
                              if (gallows.attempts == 0):
                                sendmsg("You are failed!\n Word: %s. Ha-ha-ha!\n" % (word), sock)
                                restart = True
                              else:
                                if (result[0] != 0):
                                  if (gallows.attempts != 0):
                                    if (result[0] > 0):
                                      sendmsg("Congratulations, %s you've guessed the letter [%s]!\n" % (name, usersword), sock)
                                    if (result[0] < 0) or (gallows.attempts == 0):
                                      if (result[0] == -1):
                                        sendmsg("Congratulations, %s you've guessed the word [%s]!\n" % (name, usersword), sock)
                                        restart = True
                                      if (result[0] == -2):
                                        sendmsg("Letter [%s] already opened!\n" % letter, sock)                                        
                                else:
                                  sendmsg("%s, try another letter:( [%s] %d" % (name, usersword, result[0]), sock)
                                  gallows.attempts -= 1
                              
                            except socket.error, detail:
                                logger.error(detail)
                                break
                            logger.debug(str(name) + ": " + text)
                             
                    if (restart):
                      clean()
                      word = gallows.generate()
                      usersword = word[0] + "*" * (len(word) - 2) + word[-1] 
                      logger.info("\nSecret word generated! [%s]. \nFor users: %s\n" % (word, usersword))
                      sendmsg("Secret word generated! [%s]." % str(usersword), sock)     
                      restart = False
                    
    lc=Listen_for_connections()
    

def disconnect():
  global getout
  for sock in users.keys():
    try:
      sock.send("server closed the connection")
    except error, detail:
      logger.error(detail)
    sock.close()
    del users[sock]
  sleep(1)
  logger.info("Server closed the connection\n")
  # close the mainserver
  server.close()
  logger.info("Server closed")
  sockets.append("CLOSED")

# make a server instance
s = Server()

# START the server
def start():
  s.lc.start()

