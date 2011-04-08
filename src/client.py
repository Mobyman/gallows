#-*- coding:utf-8 -*-
"""
@module: client module for gallows
@license: GNU GPL v2
@author: Egorov Ilya
@version: 0.1
"""
from socket import * 
from sys import exit
from select import select 
from time import *
from threading import *
from constants import *
from string import *
import socket, string, sys, threading, select, time, logging, constants, string, re

global HOST, PORT, LOG, usersword, connected, code, param


connected = [""]
logger = logging.getLogger("client")
logger.setLevel(logging.DEBUG)
logstream = logging.StreamHandler()
logstream.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:  %(message)s")
logstream.setFormatter(formatter)
logger.addHandler(logstream)

def answerparse(code="", param=""):
  
  lst = [""]
  parse = {}
  
  if param != "":
    param = param.strip()
    lst = param.split('_')
            
  if code == PACKET_USERWORD: #userword
    if lst.__len__() == 2:
      parse[PACKET_USERWORD] = lst
      logger.debug("Userword: %s, attempts: %s" % (lst[0], lst[1]))
    else:
      parse[PACKET_USERWORD] = None
      logger.debug("USERWORD Undefined params! [%s] Lst: %s" % (code, lst))
    return parse

  if code == ANSWER_USERCOUNT:
    if lst.__len__() == 1:
      parse[ANSWER_USERCOUNT] = lst
      logger.debug("Userscount: %s" % (lst[0]))
    else:
      parse[ANSWER_USERCOUNT] = None
      logger.debug("Userscount undefined!")
    return parse

  elif code == LETTER_FAIL or code == LETTER_WIN: #letter fail or win
    if lst.__len__() == 4:
      logger.debug("Username: %s, letter: %s, word: %s, attempts: %s" % (lst[0], lst[1], lst[2], lst[3]))
      if(code == LETTER_WIN):
        parse[LETTER_WIN] = lst
      else:
        parse[LETTER_FAIL] = lst
    else:
      parse[LETTER_FAIL] = None
      logger.debug("LETTER_FAIL_OR_WIN Undefined params! [%s] Lst: %s" % (code, lst))
    return parse
    
  elif code == LETTER_ALREADY: #letter already exists. TO-DO: Return letter (lst[0])
    parse[LETTER_ALREADY] = lst
    logger.debug("Letter already exists!")
    return parse
    
  elif code == WORD_FAIL or code == WORD_WIN: #word fail
    if lst.__len__() == 2:
      if code == WORD_FAIL:
        parse[WORD_FAIL] = lst
        logger.debug("Word fail!")
      else:
        parse[WORD_WIN] = lst
        logger.debug("Word win!")
      cli.send("", QUERY_USERWORD)
      logger.debug("Username: %s, Word: %s" % (lst[0], lst[1]))
    else:
      parse[WORD_FAIL] = None
      parse[WORD_WIN] = None
      logger.debug("WORD_FAIL_OR_WIN Undefined params! [%s] Lst: %s" % (code, lst))
    return parse
      
  elif code == CONN_CLOSE_CLI: #client close
    if lst.__len__() == 1:
      parse[CONN_CLOSE_CLI] = lst
      logger.debug("%s has been disconnected" % lst[0])
    else:
      parse[CONN_CLOSE_CLI] = None
      logger.debug("CONN_CLOSE_CLI Undefined params! [%s] Lst: %s" % (code, lst))
    return parse

  elif code == CONN_CLOSE_SERV: #server close
    cli.connected = False
    parse[CONN_CLOSE_SERV] = lst
    logger.debug("Server close connection") #lst[0] -- isAlternativeServer
    return parse
    
  elif code == CONN_CLOSE_KICK: #server close
    cli.connected = False
    logger.warning("You has been kicked!")
    parse[CONN_CLOSE_KICK] = True
 
  else:      
    logger.debug("Error code: param: %s" % (code, param))
    parse[code] = None
    return parse
  
  
class Client():
  
  parsedanswer = []
  
  def connect(self, main = True):
    self.main = main
    self.connected = False
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      if self.main:
        self.sock.connect((CLI_MAIN_HOST, CLI_MAIN_PORT))
      else: 
        sleep(3)
        logger.info("Connecting to alternative server...")
        self.sock.connect((CLI_ALT_HOST, CLI_ALT_PORT))
    except socket.error:
      if self.main:
        try:
          sleep(3)
          logger.info("Connecting to alternative server...")
          self.sock.connect((CLI_ALT_HOST, CLI_ALT_PORT))
        except socket.error:
          logger.critical("Connecting to alternative server failed...")          
          logger.critical("Servers don't worked!")
          sleep(5)
          sys.exit(0)
      else:    
        logger.critical("Servers don't worked!")
    try:
      self.sock.send(QUERY_CONN)
      self.query_result = self.sock.recv(4) 
      if (self.query_result == CONN_ALLOW):
        logger.info("Connect allowed!")
        self.connected = True
      else:
        logger.error(self.query_result) 
    except socket.error, detail:
      logger.error(detail)
      if self.main:
        cli.connect(False)
      else:
        logger.critical("Alternative server down!")
        sys.exit(0)
     
    class Listen(Thread):
      def __init__(self):
        Thread.__init__(self)
     
      def run(self):
        while True:
          try:
            data = cli.sock.recv(128)
          except socket.error, detail:
            logger.error(detail)
            cli.sock.close()
            cli.connected = False
            if cli.main:
              cli.connect(False)
            else:
              logger.critical("Alternative server down!")
              sys.exit(0)
            break
          if not data:
            if cli.main:
              cli.connect(False)
            else:
              logger.critical("Alternative server down!")
              sys.exit(0)
            break
          else:
            answer = data.strip()
            answer = answer.split("@")
            for item in answer:
              if len(item) > 0:
                if item[0] == "#":
                  code = item[:4] 
                  if code != CONN_ALLOW:
                    if len(item) > 4:
                      param = item[5:]
                      cli.parsedanswer.append(answerparse(code, param))
                    else:
                      cli.parsedanswer.append(answerparse(code))

    listen = Listen()
    listen.start()
        
    
  def send(self, msg = "", code = PACKET_LETTER):
    if self.connected == False:
      logger.error("You are not connected")
    else:
      try:
        if code == PACKET_LETTER:
          msg = msg.lower()
          if re.match("^[a-z]*$", msg):
            self.sock.send(code + "_" + str(msg))
          else:
            logger.error("Entered char not letter!")
      except socket.error, detail:
        print detail
        try:
            if self.main:
              try:
                sleep(10)
                self.sock.close()              
                logger.info("Connecting to alternative server...")
                cli.connect(False)
              except:
                cli.disconnect()  
            else: 
              cli.disconnect()            
        except NameError, detail:
          print detail

  def disconnect(self):
    global getout
    try:
      self.sock.send("#500")
    except error, detail:
      logger.error(detail)
    self.sock.close()
    sleep(1)
    logger.info("Client closed the connection\n")
    self.sock.close()
    logger.info("Client closed")
  
cli = Client()

if __name__ == '__main__':
  cli.connect()
