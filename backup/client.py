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
import socket, string, sys, threading, select, time, logging

global HOST, PORT, LOG, usersword
HOST, PORT = "localhost", 14880

global CONNECT_QUERY, ALLOW, DENY
CONNECT_QUERY = "0"
ALLOW = "1"
DENY = "-1"

logger = logging.getLogger("client")
logger.setLevel(logging.DEBUG)
logstream = logging.StreamHandler()
logstream.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:  %(message)s")
logstream.setFormatter(formatter)
logger.addHandler(logstream)

class Client():

  def connect(self):
    self.connected = [False]
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((HOST, PORT))
    logging.error("You are already connected!")
    try:
      self.sock.send("CONNECT_QUERY")
      self.query_result = self.sock.recv(1024)
      if (self.query_result == "SUCCESS"):
        logging.info(self.query_result)
        connected.append(True)
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
          if not data: break
          else: print data
    listen = Listen()
    listen.start()
        
  
  def send(self, msg = ""):
    if self.connected == False:
      logging.error("You are not connected")
    else:
      if msg == "":
        msg = raw_input("Enter letter:")
      try:
        self.sock.send(msg)
      except socket.error, detail:
        print detail
      except NameError, detail:
        print detail

cli = Client()
