# -*- coding: utf-8 -*-

"""
@module: server module for gallows
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
from constants import *
import socket, string, sys, threading, select, time, logging, constants, re, pickle

global HOST, PORT, LOG, usersword, ATTEMPT_MAX, USERNAME, ALT_SERVER

ALT_SERVER = False
HOST, PORT = "localhost", 14880
ATTEMPT_MAX = 10
USERNAME = "Prisoner"
logger = logging.getLogger("server")
logger.setLevel(logging.DEBUG)
logstream = logging.StreamHandler()
logstream.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:  %(message)s")
logstream.setFormatter(formatter)
logger.addHandler(logstream)

def pack(obj):
  p = pickle.dumps(obj)
  print p

def sendmsg(msg, adr):
  for sock in users.keys():
    sock.send(msg)

def clean():
  userscount = 0
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
    if (uword.count(letter) > 0):
      logger.info("Letter already opened")
      guessed = -2
      newuword = uword
    else:
      iter1 = True # Edit strings %)
      guessed = self.secret.count(letter)
      print self.secret, guessed, letter, "<<<<"
      tmp2 = uword
      for x in range(len(self.secret)):
        if (self.secret.find(letter) != -1):
            pos = self.secret.find(letter)
            tmp = self.secret
            logger.debug("Position:" + str(pos))
            self.secret = tmp[:pos] + "@" + tmp[pos + 1:]
            if (iter1):
              tmp2 = uword[:pos] + letter + uword[pos + 1:]
            else:
              tmp2 = tmp2[:pos] + letter + tmp2[pos + 1:]
        iter1 = False
      logger.info("Letter %s; Attempts: %d" % (letter, self. attempts))
      if tmp2.count("*") == 0:
        guessed = -1
      newuword = tmp2
    logger.info("New user word: %s" % newuword)
    return [guessed, newuword]


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
                            break
                        if not text:
                            sendmsg(CONN_CLOSE_CLI + "_%s@" % name, sock)
                            logger.info(name + " has been disconnected!")
                            sleep(1)
                            userscount -= 1
                            sock.close()
                            del users[sock]
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
                                    break

                                  lst = item.split("_")

                                  if lst[0] == QUERY_USERWORD:
                                    sock.send(PACKET_USERWORD + "_%s_%s@" % (usersword, gallows.attempts))
                                    restart = True

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
                                        pack(gallows)
                                      break
                                  if lst[0] == QUERY_USERWORD:
                                    sendmsg(PACKET_USERWORD + "_%s_%s@" % (usersword, gallows.attempts), sock)
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


def disconnect():
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

# make a server instance
s = Server()

# START the server
def start():
  s.lc.start()

start()
