# -*- coding: utf-8 -*-
import os
import telebot
import time
import telebot
import random
import info
import threading
from emoji import emojize
from telebot import types
from pymongo import MongoClient
from emoji import emojize


token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)

games={}

client=MongoClient(os.environ['database'])
db=client.neiro
match=db.match


symbollist=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
           '1','2','3','4','5','6','7','8','9','0']


@bot.message_handler(commands=['create'])
def create(m):
    if m.chat.id not in games:
        games.update(creategame(m.chat.id))


def creategame(id):
    return{id:{'id':id,
               'players':{},
               'currentposition':None
              }
          }
        
        
if True:
   print('7777')
   bot.polling(none_stop=True,timeout=600)

