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
import socket, threading, select, logging, gallows_logic, re

global HOST, PORT, LOG, usersword, ATTEMPT_MAX, USERNAME, ALT_SERVER, pong

ALT_SERVER = False
HOST, PORT = ("localhost", 14880)
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

class Ponger(Thread):
  
  def __init__(self):
      Thread.__init__(self)
  
  def run(self):
      try:
        pong = socket.socket(AF_INET, SOCK_STREAM)
        pong.bind((HOST, 14881))
        logger.debug("Ponger server binded")
        pong.listen(1)
        logger.debug("Ponger server listen on port " + str(14881))
      except socket.error, detail:
        logger.error(detail)
      pingsock, addr = pong.accept()
      logger.info("Ponger connected %s" % str(addr))
      try:
        while True:
          data = pingsock.recv(128)
          ping = data.strip()
          ping = ping.split("@")
          if not data: logger.info("Pong server error! %s" % pingsock.fileno())
          else:           
            for item in ping:
              if len(ping) > 0:
                if item[0] == "#":
                  code = item[:5] 
                  if code == CONN_PING:
                      pingsock.send(CONN_PONG)
                      logger.info("Pong server success! %s" % pingsock.fileno())
                      sleep(5)
      except socket.error, detail:
        logger.info("Pong server error! %s" % pingsock.fileno())        

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
                        #if (userscount > 1):
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
                                    word = gallows.generate()
                                    usersword = "*" * len(word)
                                    logger.info("\nSecret word generated! [%s]. \nFor users: %s\n" % (word, usersword))
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

    ponger = Ponger()
    ponger.start()
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