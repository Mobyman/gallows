# -*- coding: utf-8 -*-

"""
@module: constants for server protocol gallows
@license: GNU GPL v2
@author: Egorov Ilya
@version: 0.7
"""

global QUERY_CONN, CONN_ALLOW, CONN_DENY, \
PACKET_SIZE, PACKET_LETTER, PACKET_ALLOW, PACKET_USERWORD, \
LETTER_FAIL, LETTER_WIN, WORD_FAIL, WORD_WIN, \
CONN_CLOSE_CLI, CONN_CLISE_SERV

QUERY_CONN          = "#100"
CONN_ALLOW          = "#111"
CONN_DENY           = "#110"

PACKET_SIZE         = "#200"

PACKET_LETTER       = "#201"
PACKET_ALLOW        = "#211"

QUERY_USERWORD      = "#203"
PACKET_USERWORD     = "#213"

QUERY_USERCOUNT     = "#204"
ANSWER_USERCOUNT    = "#214"

QUERY_USEDLETTERS   = "#205"
ANSWER_USEDLETTERS  = "#215"

LETTER_FAIL         = "#310"
LETTER_WIN          = "#311"
LETTER_ALREADY      = "#320"

WORD_FAIL           = "#410"
WORD_WIN            = "#411"

CONN_CLOSE_CLI      = "#500"
CONN_CLOSE_SERV     = "#510"
CONN_CLOSE_KICK     = "#511"

CONN_PING           = "#ping"
CONN_PONG           = "#pong"