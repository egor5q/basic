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

aibattle=0


symbollist=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
           '1','2','3','4','5','6','7','8','9','0']


@bot.message_handler(commands=['enableai'])
def enableai(m):
    global aibattle
    aibattle=1

@bot.message_handler(commands=['create'])
def create(m):
    if m.chat.id not in games:
        games.update(creategame(m.chat.id))
        bot.send_message(m.chat.id, '/join')
    else:
        bot.send_message(m.chat.id, 'ошибка')

@bot.message_handler(commands=['join'])
def join(m):
    no=0
    if m.chat.id in games:
      if games[m.chat.id]['started']==0:
        for ids in games[m.chat.id]['players']:
            if games[m.chat.id]['players'][ids]['id']==m.from_user.id:
                no=1
    if len(games[m.chat.id]['players'])<1:
      if no==0:
        try:
            bot.send_message(m.from_user.id, 'Вы успешно присоединились!')
            games[m.chat.id]['players'].update(createplayer(m.from_user.id, m.from_user.first_name, m.from_user.username,0))
            bot.send_message(m.chat.id, m.from_user.first_name+' присоединился!')
        except:
            bot.send_message(m.chat.id, 'Для начала напишите боту что-нибудь!')
      else:
           bot.send_message(m.chat.id, 'Вы уже в игре!')
    else:
        bot.send_message(m.chat.id, 'Достигнуто максимальное число игроков!')     
      
    
@bot.message_handler(commands=['startii'])
def startii(m):
    if m.chat.id not in games:
        games.update(creategame(m.chat.id))
        bot.send_message(m.chat.id, 'Игра ИИ началась.')
        games[m.chat.id]['players'].update(createplayer('ai','bot','bot',1))
        games[m.chat.id]['players'].update(createplayer('ai2','bot','bot',1))
        global aibattle
        if aibattle==1:
            begin(m.chat.id)
    

    
def begin(id):
    if id in games:
        i=random.randint(0,1)
        for ids in games[id]['players']:
            player=games[id]['players'][ids]
            if i==0:
                player['role']='x'
                i=1
            else:
                player['role']='o'
                i=0
        xod(id)
    

                        
def xod(id):

    
    
    
    
    
def creategame(id):
    return{id:{'id':id,
               'players':{},
               'currentposition':[],
               'alllocs':[1,2,3,4,5,6,7,8,9],
               'emptylocs':[1,2,3,4,5,6,7,8,9]
              }
          }
       
    
def createplayer(id,name,username,bott):
    return{id:{'name':name,
               'id':id,
               'username':username,
               'locs':[],
               'isbot':bott,
               'role':None,
               'myturn':0
              }
          }
               
    
        
if True:
   print('7777')
   bot.polling(none_stop=True,timeout=600)

