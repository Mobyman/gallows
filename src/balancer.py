# -*- coding: utf-8 -*-

"""
@module: balancer module for gallows
@license: GNU GPL v2
@author: Egorov Ilya
@version: 0.001
"""
from socket import *
from threading import *
from select import select
from constants import *
from time import sleep
import socket, threading, select, logging

global SERVERS
SERVERS = {0: ("localhost", 14881)}

logger = logging.getLogger("balancer")
logger.setLevel(logging.DEBUG)
logstream = logging.StreamHandler()
logstream.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
logstream = logging.StreamHandler()
logstream.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:  %(message)s")
logstream.setFormatter(formatter)
logger.addHandler(logstream)

class Pinger(Thread):

  def __init__(self):
    Thread.__init__(self)
    self.connected = False

  def run(self):
   self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #for server in SERVERS.keys():
   self.sock.connect(("localhost", 14881))
   while True:
    try:
      self.sock.send(CONN_PING)
      data = self.sock.recv(5)
      sleep(5)
    except socket.error, detail:
      logging.error(detail)
      self.connected = False
      logger.info("Ping server error! %s" % self.sock.fileno())
      break
    if not data: logger.info("Ping server error! %s" % self.sock.fileno())
    else:
      answer = data.strip()
      answer = answer.split("@")
      for item in answer:
        if len(item) > 0:
          if item[0] == "#":
            code = item[:5] 
            if code == CONN_PONG:
                logger.info("Ping server success! %s" % self.sock.fileno())
            else:
                logger.info("Ping server error! %s %s" % (self.sock.fileno(), str(code)))
  
pinger = Pinger()
pinger.start()                  
