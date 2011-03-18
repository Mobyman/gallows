# -*- coding: utf-8 -*-

"""
@module: balancer module for gallows
@license: GNU GPL v2
@author: Egorov Ilya
@version: 0.001
"""
class Balancer:

  global SERVERS
  SERVERS = { 0 : {"host": "localhost", "port": 14880}}
  
  class Pinger(Thread):
    
    def __init__(self):
      Thread.__init__(self)
      
    def run():
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      for server in SERVERS.keys():
        self.sock.connect((server["host"], server["port"]))

  class Coordination:
