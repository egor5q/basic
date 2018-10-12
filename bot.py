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

#client1=os.environ['database']
#client=MongoClient(client1)
#db=client.spyvssecurity
#users=db.users


symbollist=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
           'а','б','в','г','д','е','ё','ж','з','и','й','к','л','м','н','о','п','р','с','т','у','ф','х','ц','ч','ш','щ','ъ','ы','ь','э','ю','я',
           '1','2','3','4','5','6','7','8','9','0']


@bot.message_handler(commands=['creategame'])
def creategamee(m):
    if m.chat.id not in games:
        games.update(creategame(m.chat.id))
        bot.send_message(m.chat.id, 'Жмите /join, чтобы присоединиться! До отмены игры 5 минут.')
        t=threading.Timer(300,cancelgame,args=[m.chat.id])
        t.start()
        games[m.chat.id]['timer']=t
        
        
@bot.message_handler(commands=['startgame'])
def startg(m):
    if m.chat.id in games:
        if len(games[m.chat.id]['players'])==2:
            games[m.chat.id]['timer'].cancel()
            begin(m.chat.id)
            
            
def begin(id):
    securityitems=['glasses','pistol','tizer']
    spyitems=['camera','camera','camera','flash','costume']
    for ids in games[id]['players']:
        if games[id]['spies']>games[id]['security']:
            games[id]['players'][ids]['role']='security'
            games[id]['security']+=1
        elif games[id]['spies']<games[id]['security']:
            games[id]['players'][ids]['role']='spy'
            games[id]['spies']+=1
        elif games[id]['spies']==games[id]['security']:
            x=random.choice(['spy','security'])
            games[id]['players'][ids]['role']=x
            if x=='spy':
                games[id]['spies']+=1
            elif x=='security':
                games[id]['security']+=1
                
    for ids in games[id]['players']:
        if games[id]['players'][ids]['role']=='security':
            games[id]['players'][ids]['items']=securityitems
            games[id]['players'][ids]['location']='treasure'
        elif games[id]['players'][ids]['role']=='spy':
            games[id]['players'][ids]['items']=spyitems
            games[id]['players'][ids]['location']='spystart'
            
    for ids in games[id]['players']:
        sendacts(games[id]['players'][ids])
        
    t=threading.Timer(90, endturn, args=[id])
        
def endturn(id):
    for ids in games[id]['players']:
        if games[id]['players'][ids]['ready']==0:
            medit('Время вышло!',games[id]['players'][ids]['messagetoedit'].chat.id, games[id]['players'][ids]['messagetoedit'].message_id)
    pass


def sendacts(player):  
    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Перемещение', callback_data='move'),types.InlineKeyboardButton(text='Предметы', callback_data='items'))
    if player['role']=='spy':
        kb.add(types.InlineKeyboardButton(text='Инфо с камер', callback_data='camerainfo'))
    kb.add(types.InlineKeyboardButton(text='Ожидать', callback_data='wait'))
    msg=bot.send_message(player['id'],'Выберите действие.',reply_markup=kb)
    player['messagetoedit']=msg
               
     
               
def cancelgame(id):
    try:
        del games[id]
        bot.send_message(id, 'Игра была отменена!')
    except:
        pass
    

def medit(message_text,chat_id, message_id,reply_markup=None,parse_mode='Markdown'):
    return bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=message_text,reply_markup=reply_markup,
                                 parse_mode=parse_mode)


@bot.callback_query_handler(func=lambda call:True)
def inline(call):
  yes=0
  for ids in games:
    for idss in games[ids]['players']:
        if games[ids]['players'][idss]['id']==call.from_user.id:
            yes=1
            player=games[ids]['players'][idss]
  if yes==1:
    kb=types.InlineKeyboardMarkup()
    if call.data=='move':
        if player['location']=='spystart':
            kb.add(types.InlineKeyboardButton(text='Левый корридор', callback_data='leftcorridor'),types.InlineKeyboardButton(text='Правый корридор', callback_data='rightcorridor'))
            kb.add(types.InlineKeyboardButton(text='Левый обход', callback_data='leftpass'),types.InlineKeyboardButton(text='Правый обход', callback_data='rightpass'))
            
        if player['location']=='treasure':
            kb.add(types.InlineKeyboardButton(text='Левый корридор', callback_data='leftcorridor'),types.InlineKeyboardButton(text='Правый корридор', callback_data='rightcorridor'))
            kb.add(types.InlineKeyboardButton(text='Левый обход', callback_data='leftpass'),types.InlineKeyboardButton(text='Правый обход', callback_data='rightpass'))
            kb.add(types.InlineKeyboardButton(text='Светозащитная комната', callback_data='antiflashroom'))
            
        if player['location']=='leftcorridor':
            kb.add(types.InlineKeyboardButton(text='Левый обход', callback_data='leftpass'),types.InlineKeyboardButton(text='Старт шпионов', callback_data='spystart'))
            
        if player['location']=='rightcorridor':
            kb.add(types.InlineKeyboardButton(text='Правый обход', callback_data='rightpass'),types.InlineKeyboardButton(text='Старт шпионов', callback_data='spystart'))
        



def creategame(id):
    return{
        'chatid':id,
        'players':{},
        'turn':1,
        'spies':0,
        'security':0,
        'timer':None,
        'locs':['treasure','spystart','leftcorridor','rightcorridor','leftpass','rightpass','antiflashroom']
    }

def createplayer(id,name):
    return{
        'id':id,
        'name':name,
        'location':None,
        'team':None,
        'items':[],
        'ready':0,
        'messagetoedit':None
    }



if True:
   print('7777')
   bot.polling(none_stop=True,timeout=600)

