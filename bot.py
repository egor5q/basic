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


token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)


client=MongoClient(os.environ['database'])
db=client.survivals
users=db.users

symbollist=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
           'а','б','в','г','д','е','ё','ж','з','и','й','к','л','м','н','о','п','р','с','т','у','ф','х','ц','ч','ш','щ','ъ','ы','ь','э','ю','я', ' ']




@bot.message_handler()
def allmessages(m):
    start=0
    if users.find_one({'id':m.from_user.id})==None:
        users.insert_one(createuser(m.from_user.id,m.from_user.first_name,m.from_user.username))
        start=1
    user=users.find_one({'id':m.from_user.id})
    if start==1:
        bot.send_message(m.chat.id, 'Здраствуй, выживший! Назови своё имя.')
        users.update_one({'id':user['id']},{'$push':{'effects':'setname'}})
    else:
        if 'setname' in user['effects']:
            no=0
            for ids in m.text:
                if ids not in symbollist:
                    no=1
            if no==0:
                users.update_one({'id':user['id']},{'$set':{'heroname':m.text}})
                bot.send_message(m.chat.id, 'Добро пожаловать в отряд, '+m.text+'! Чтобы противостоять армиям зомби, тебе '+
                                'понадобится оружие. На, держи!')
                bot.send_message(m.chat.id, 'Получено: *пистолет*')
                users.update_one({'id':user['id']},{'$push':{'inventory':'pistol'}})
                time.sleep(2)
                bot.send_message(m.chat.id, 'Со всей нашей командой ты можешь познакомиться здесь: @неизветно. Ладно, хватит '+
                                'слов - зомби наступают! Пошли, будешь помогать обороняться.')#@Survivalschat. ')
                t=threading.Timer(2,defcamp,args=[user])
                t.start()
                      
       
def defcamp(user):
    pass
    

def createuser(id,name,username):
    return {'id':{
        'name':name,
        'heroname':None,
        'id':id,
        'username':username,
        'effects':[],
        'inventory':[]
    
    }

if True:
   print('7777')
   bot.polling(none_stop=True,timeout=600)

