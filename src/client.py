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
import socket, string, sys, threading, select, time, logging, constants, string

global HOST, PORT, LOG, usersword, connected, code, param
HOST, PORT = "localhost", 14880
connected = [""]
logger = logging.getLogger("client")
logger.setLevel(logging.DEBUG)
logstream = logging.StreamHandler()
logstream.setLevel(logging.DEBUG)

def answerparse(code = "", param = ""):
  
  lst = [""]
  
  if param != "":
    param = param.strip()
    lst = param.split('_')
          
  if code == PACKET_USERWORD: #userword
    if lst[0] and lst[1]:
      logger.debug("Userword: %s, attempts: %s" % (lst[0], lst[1]))
    else:
      logger.debug("Undefined params! [%s] Lst: %s" % (code, lst))
    
  elif code == LETTER_FAIL or LETTER_WIN: #letter fail or win
    if lst.__len__() > 3:
      logger.debug("Username: %s, letter: %s, word: %s, attempts: %s" % (lst[0], lst[1], lst[2], lst[3]))
      if(code == LETTER_WIN):
        return 1
      else:
        return 0
    else:
      logger.debug("Undefined params! [%s] Lst: %s" % (code, lst))
      
  elif code == LETTER_ALREADY: #letter already exists
    logger.debug("Letter already exists!")
    
  elif code == WORD_FAIL or WORD_WIN: #word fail
    if lst[0] and lst[1]:
      if code == WORD_FAIL:
        logger.debug("Word fail!")
      else:
        logger.debug("Word win!")
      logger.debug("Username: %s, Word: %s" % (lst[0], lst[1]))
    else:
      logger.debug("Undefined params! [%s] Lst: %s" % (code, lst))
      
  elif code == CONN_CLOSE_CLI: #client close
    if lst[0]:       
      logger.debug("%s has been disconnected" % lst[0])
    else:
      logger.debug("Undefined params! [%s] Lst: %s" % (code, lst))      
  
  elif code == CONN_CLOSE_SERV: #server close
    logger.debug("Server close connection" % lst[0]) #lst[0] -- isAlternativeServer
  else:      
    logger.debug("Error code: param: %s" % (code, param))
    
class Client():
  
  connected = [""]
  def connect(self):
    self.connected = False
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((HOST, PORT))
    logging.info("You are connected!")
    try:
      self.sock.send(QUERY_CONN)
      self.query_result = self.sock.recv(4) 
      if (self.query_result == CONN_ALLOW):
        logger.info("Connect allowed!")
        connected = True
      else:
        logging.error(self.query_result) 
    except socket.error, detail:
      logging.error(detail)
     
    class Listen(Thread):
      def __init__(self):
        Thread.__init__(self)
     
      def run(self):
        while True:
          try:
            data = cli.sock.recv(1024)
          except socket.error, detail:
            logging.error(detail)
            cli.sock.close()
            cli.connected = False
            #Alternative server connecting
            break
          if not data: break
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
                      answerparse(code, param)
                    else:
                      answerparse(code)

    listen = Listen()
    listen.start()
        
  
  def send(self, code = "#201", msg = ""):
    if self.connected == False:
      logging.error("You are not connected")
    else:
      try:
        self.sock.send(code + " " + str(msg))
      except socket.error, detail:
        print detail
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
cli.connect()
