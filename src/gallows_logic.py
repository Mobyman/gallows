# -*- coding: utf-8 -*-

"""
@module: game-logic module for gallows
@license: GNU GPL v2
@author: Egorov Ilya
@version: 0.7
"""
from string import *
from threading import *
from random import randrange
import string, threading, time, logging

global HOST, PORT, LOG, usersword, ATTEMPT_MAX, USERNAME, ALT_SERVER

ALT_SERVER = False
HOST, PORT = "localhost", 14880
ATTEMPT_MAX = 10
USERNAME = "Prisoner"

logger = logging.getLogger("gallows")
logger.setLevel(logging.DEBUG)
logstream = logging.StreamHandler()
logstream.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:  %(message)s")
logstream.setFormatter(formatter)
logger.addHandler(logstream)

class Gallows:

  def __init__(self):
    self.attempts = ATTEMPT_MAX
    self.generated = False

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
    self.used_letters = []
    self.generated = True
    logger.debug("Generated TRUE")
    self.newuword = "*" * len(self.secret)
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
    if (uword.count(letter) > 0) or (self.used_letters.count(letter) > 0):
      logger.info("Letter already opened")
      guessed = -2
      self.newuword = uword
    else:
      self.used_letters.append(letter)
      iter1 = True 
      guessed = self.secret.count(letter)
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
      self.newuword = tmp2
    logger.info("New user word: %s" % self.newuword)
    return [guessed, self.newuword]