# -*- coding: utf-8 -*-

"""
@module: server protocol module for gallows
@license: GNU GPL v2
@author: Egorov Ilya
@version: 0.7
"""
from socket import *
from threading import *
from select import select
from constants import *
from gallows_logic import *
from time import sleep
from optparse import OptionParser
from sys import exit
import socket, threading, select, logging, gallows_logic, re, sys

global HOST, PORT, LOG, usersword, ATTEMPT_MAX, USERNAME, main_server, pong

HOST_PING,  PORT_PING = ("localhost", 14881)
HOST_PONG,  PORT_PONG = ("localhost", 14881)
MAIN_HOST,  MAIN_PORT = ("localhost", 14879) 
ALT_HOST,   ALT_PORT =  ("localhost", 14880)

ATTEMPT_MAX = 10
USERNAME = "Prisoner"
logger = logging.getLogger("server_protocol")
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
  userscount = 0
  users = {}
  sockets = [""]
  gallows.attempts = ATTEMPT_MAX


class Pinger(Thread):

  def __init__(self):
    Thread.__init__(self)
    self.packets = None
    
  def parsesync(self, packets):
    packets = packets[0].split("_")
    if (len(packets) == 5) and (packets[0] == SYNC_SERVER_PACKET):
      self.secret   = packets[1]
      self.attempts = int(packets[2])
      self.userword = packets[3]        
      self.used_letters = list(packets[4])
      start()
  
  def run(self):
    try:
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.connect((HOST_PING, PORT_PING))
    except:
      logger.critical("Main server don't work!")
      sys.exit(0)
    while True:
      try:
        self.sock.send(CONN_PING + "@")
        data = self.sock.recv(128)
      except socket.error, detail:
        logging.error(detail)
        logger.error("Ping server error! %s" % self.packets)      
        if self.packets:
          self.parsesync(self.packets)
        break
      if not data: logger.error("Ping server error! %s" % self.sock.fileno())
      else:
        try:
          self.packets = data.strip()
          self.packets = self.packets.split("$")
          for pack in self.packets:
            answers = pack.strip()
            answers = pack.split("_")
            for item in answers:
              if len(item) > 0:
                if item[0] == "#":
                  code = item[:4] 
                  if code == CONN_PONG:
                    logger.info("Ping server success! %s" % self.sock.fileno())
                    self.sock.send(CONN_PING + "$")
                  elif code == SYNC_SERVER_PACKET:
                    print "SYNC: " + str(answers)
                    self.sock.send(SYNC_SERVER_PACKET_APPLY + "$")
                  else:
                    logger.error("Ping server error! CODE: '%s'" % code)
                    self.parsesync(self.packets)
        except socket.error:
          logger.error("Ping server error! %s" % self.packets)
          self.parsesync(self.packets)        

class Ponger(Thread):
  
  def __init__(self):
      Thread.__init__(self)
      
  def run(self):
      try:
        pong = socket.socket(AF_INET, SOCK_STREAM)
        pong.bind((HOST_PONG, PORT_PONG))
        logger.debug("Ponger server binded")
        pong.listen(5)
        logger.debug("Ponger server listen on port " + str(PORT_PONG))
        sleep(15)
      except socket.error, detail:
        logger.error(detail)
      pingsock, addr = pong.accept()
      logger.info("Ponger connected %s" % str(addr))
      try:
        while True:
          data = pingsock.recv(32)
          ping = data.strip()
          ping = ping.split("$")
          if not data: logger.error("Pong server error! %s" % pingsock.fileno())
          else:           
            for item in ping:
              if len(ping) > 0:
                if len(item) > 0:
                  if item[0] == "#":
                    code = item[:4] 
                    if code == CONN_PING:
                      if hasattr(gallows, 'secret'):
                        pingsock.send(SYNC_SERVER_PACKET + "_%s_%s_%s_%s$" % (gallows.secret, str(gallows.attempts), gallows.newuword, str(gallows.used_letters)))
                        logger.info("Send: " + SYNC_SERVER_PACKET + "_%s_%s_%s_%s$" % (gallows.secret, str(gallows.attempts), gallows.newuword, str(gallows.used_letters)))
                        sleep(2)
                      else:
                        pingsock.send(CONN_PONG + "$")
                        sleep(2)
                        break
                    elif code == SYNC_SERVER_PACKET_APPLY:
                        logger.info("SYNC OK! %s" % pingsock.fileno())
                    elif item[0] != "#":
                        break
                    else:
                        logger.info("Pong server unknown answer code! CODE: %s" % code)        
      except socket.error, detail:
        logger.error("Pong server error! %s" % pingsock.fileno())        

class Server:
    # listen for connections
    
    class Listen_for_connections(Thread):
        def __init__(self):
            Thread.__init__(self)
        
        def run(self):
            global users, server, rl, sockets, userscount, gallows, queue_start, usersword, letter
            gallows = Gallows()
            queue_start = []
            try:
                server = socket.socket(AF_INET, SOCK_STREAM)
                server.bind((HOST, PORT))
                logger.debug("Server binded")
                server.listen(1)
                logger.debug("Server listen")
            except socket.error, detail:
                logger.error(detail)
            USERNAME = "Prisoner"
            userscount = 0
            users = {}
            sockets = [""]
            restart = False
            result = []
            guessed = 0
            fail = {}
            kick = False
            while True:
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
                        users[sock] = USERNAME + str(userscount)
                        userscount += 1
                        new = sock
                    else:
                        for sock in users.keys():
                            if sock.fileno() == n: break
                        name = users[sock]
                        try:
                            text = sock.recv(128)
                            parse = text.split("@")
                        except socket.error, detail:
                            userscount -= 1
                            logger.info(name + " has been disconnected!")
                            del users[sock]
                            sendmsg(ANSWER_USERCOUNT + "_%s@" % (userscount), sock)

                            break
                        if not text:
                            logger.info(name + " has been disconnected!")
                            sleep(1)
                            userscount -= 1
                            sock.close()
                            del users[sock]
                            sendmsg(ANSWER_USERCOUNT + "_%s@" % (userscount), sock)                            
                        else:
                            try:
                              for item in parse:
                                if item[0] == "#":
                                  if text[0:4] == QUERY_CONN:
                                    sock.send(CONN_ALLOW + "@")
                                    queue_start.append(sock)
                                    if main_server:
                                      word = gallows.generate()
                                      usersword = "*" * len(word)
                                      logger.info("\nSecret word generated! [%s]. \nFor users: %s\n" % (word, usersword))
                                    else:
                                      gallows.secret   = pinger.secret
                                      gallows.attempts = pinger.attempts
                                      gallows.newuword = pinger.userword
                                      usersword = pinger.userword
                                      gallows.newuword = pinger.userword
                                      gallows.used_letters = pinger.used_letters 
                                    sendmsg(PACKET_USERWORD + "_%s_%s@" % (usersword, gallows.attempts), sock)
                                    sendmsg(ANSWER_USERCOUNT + "_%s@" % (userscount), sock)
                                    break
                                    
                                  lst = item.split("_")
                                  logger.debug(lst)
                                  if lst[0] == QUERY_USERWORD:
                                    sock.send(PACKET_USERWORD + "_%s_%s@" % (usersword, gallows.attempts))
                                    restart = True
                                  
                                  if lst[0] == QUERY_USERCOUNT:
                                    sendmsg(ANSWER_USERCOUNT + "_%s@" % (userscount), sock)
                                    logger.info("Userscount is %s" % (userscount))
                                      
                                  if lst[0] == PACKET_LETTER:
                                    if len(lst[1])== 1 and re.match("^[a-z]*$", lst[1]):
                                      letter = lst[1]
                                      result = gallows.getletter(usersword, strip(letter))
                                      logger.info("S: %s UW: %s Text: %s Letter: %s Result: %s" % (gallows.secret, usersword, text, letter, result))
                                      usersword = result[1]

                                      if (gallows.attempts == 0):
                                        sendmsg(WORD_FAIL + "_%s_%s@" % (name, word), sock)
                                        restart = True
                                      else:
                                        if (result[0] != 0):
                                          if (gallows.attempts != 0):
                                            if (result[0] > 0):
                                              sendmsg(LETTER_WIN + "_%s_%s_%s_%s@" % (name, letter, usersword, gallows.attempts), sock)
                                            if (result[0] < 0) or (gallows.attempts == 0):
                                              if (result[0] == -1):
                                                sendmsg(WORD_WIN + "_%s_%s@" % (name, usersword), sock)
                                                restart = True
                                              if (result[0] == -2):
                                                sendmsg(LETTER_ALREADY + "_%s@" % letter, sock)
                                        else:
                                          sendmsg(LETTER_FAIL + "_%s_%s_%s_%s@" % (name, letter, usersword, gallows.attempts), sock)
                                          gallows.attempts -= 1
                                      for sock in queue_start:
                                        sendmsg(PACKET_USERWORD + "_%s_%s@" % (usersword, gallows.attempts), sock)
                                      break
                                  if lst[0] == QUERY_USERWORD:
                                    sendmsg(PACKET_USERWORD + "_%s_%s@" % (usersword, gallows.attempts), sock)
                                    logger.info("Userscount is %s" % (userscount))
                                    
                                  else:
                                    kick = True
                                else:
                                  kick = True
                            except socket.error, detail:
                                logger.error(detail)
                                break
                            logger.debug(str(name) + ": " + text)

                    if (kick):
                      logger.info("Client %s kicked!" % name)
                      sock.send(CONN_CLOSE_KICK)
                      userscount -= 1
                      del users[sock]
                      new = None
                      sendmsg(ANSWER_USERCOUNT + "_%s@" % (userscount), sock)
                      sock.close()

                    if (new == sock):
                      sock.send(CONN_ALLOW)

                    if (restart):
                      clean()
                      word = gallows.generate()
                      usersword = "*" * len(word)
                      logger.info("\nSecret word generated! [%s]. \nFor users: %s\n" % (word, usersword))
                      sendmsg(PACKET_USERWORD + "_%s_%s@" % (usersword, gallows.attempts), sock)
                      restart = False
  
    lc = Listen_for_connections()


    def disconnect(self):
      global getout
      for sock in users.keys():
        try:
          sock.send("#510")
        except error, detail:
          logger.error(detail)
        sock.close()
        del users[sock]
      sleep(1)
      logger.info("Server closed the connection\n")
      server.close()
      logger.info("Server closed")
      sockets.append("CLOSED")


parser = OptionParser()
parser.add_option("-t", "--type", dest="type", help="--- SERVER TYPE --- ""Main server: -t m""Alternative server: -t a")
(options, args) = parser.parse_args()

s = Server()         

def start():
  s.lc.start()
  print "Started..."

if (options.type == "a"):
  HOST, PORT = (ALT_HOST, ALT_PORT)
  pinger = Pinger()
  pinger.start()    
  main_server = False
  
elif (options.type == "m"):    
  HOST, PORT = (MAIN_HOST, MAIN_PORT)
  ponger = Ponger()
  ponger.start()
  main_server = True
  start()
else: sys.exit(0)
 
