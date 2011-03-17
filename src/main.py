# -*- coding: utf-8 -*-

"""
@module: main server module for gallows
@license: GNU GPL v2
@author: Egorov Ilya
@version: 0.7
"""

from protocol_server import *
import protocol_server

global HOST, PORT, LOG, usersword, ATTEMPT_MAX, USERNAME, ALT_SERVER

ALT_SERVER = False
HOST, PORT = "localhost", 14880
ATTEMPT_MAX = 10
USERNAME = "Prisoner"
logger = logging.getLogger("main_server")
logger.setLevel(logging.DEBUG)
logstream = logging.StreamHandler()
logstream.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:  %(message)s")
logstream.setFormatter(formatter)
logger.addHandler(logstream)

# make a server instance
s = Server()

# START the server
def start():
  s.lc.start()

start()
