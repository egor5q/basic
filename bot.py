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
history={}
#client1=os.environ['database']
#client=MongoClient(client1)
#db=client.spyvssecurity
#users=db.users


symbollist=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
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
      if games[m.chat.id]['started']==0:
        if len(games[m.chat.id]['players'])==2:
            games[m.chat.id]['started']=1
            games[m.chat.id]['timer'].cancel()
            begin(m.chat.id)
    
@bot.message_handler(commands=['join'])
def join(m):
    no=0
    if m.chat.id in games:
      if games[m.chat.id]['started']==0:
        for ids in games[m.chat.id]['players']:
            if games[m.chat.id]['players'][ids]['id']==m.from_user.id:
                no=1
    if no==0:
        try:
            bot.send_message(m.from_user.id, 'Вы успешно присоединились!')
            games[m.chat.id]['players'].update(createplayer(m.from_user.id, m.from_user.first_name, m.chat.id))
            bot.send_message(m.chat.id, m.from_user.first_name+' присоединился!')
        except:
            bot.send_message(m.chat.id, 'Для начала напишите боту @Spy_VS_Security_Bot что-нибудь!')
    
 
def testturn(id):
    i=0
    for ids in games[id]['players']:
        if games[id]['players'][ids]['ready']==1:
           i+=1
    if i==len(games[id]['players']):
           games[id]['gametimer'].cancel()
           endturn(id)
            
def begin(id):
    securityitems=['glasses','pistol','tizer', 'glasses']
    spyitems=['camera','camera','camera','flash','costume', 'flash']
    for ids in games[id]['players']:
        if games[id]['spies']>games[id]['security']:
            games[id]['players'][ids]['role']='security'
            games[id]['security']+=1
            bot.send_message(games[id]['players'][ids]['id'], 'Вы - охранник! Ваша цель - не дать шпионам украсть сокровище!'+\
                             'Если продержитесь 15 ходов - вам на помощь приедет спецназ, и вы победите!')
        elif games[id]['spies']<games[id]['security']:
            games[id]['players'][ids]['role']='spy'
            games[id]['spies']+=1
            bot.send_message(games[id]['players'][ids]['id'], 'Вы - шпион! Ваша цель - украсть сокровище!'+\
                             'Не попадитесь на глаза охраннику и сделайте всё меньше, чем за 16 ходов, иначе проиграете!')
        elif games[id]['spies']==games[id]['security']:
            x=random.choice(['spy','security'])
            games[id]['players'][ids]['role']=x
            if x=='spy':
                games[id]['spies']+=1
                bot.send_message(games[id]['players'][ids]['id'], 'Вы - шпион! Ваша цель - украсть сокровище!'+\
                             'Не попадитесь на глаза охраннику и сделайте всё меньше, чем за 16 ходов, иначе проиграете!')
            elif x=='security':
                games[id]['security']+=1
                bot.send_message(games[id]['players'][ids]['id'], 'Вы - охранник! Ваша цель - не дать шпионам украсть сокровище!'+\
                             'Если продержитесь 15 ходов - вам на помощь приедет спецназ, и вы победите!')
                
    for ids in games[id]['players']:
        if games[id]['players'][ids]['role']=='security':
            games[id]['players'][ids]['items']=securityitems
            games[id]['players'][ids]['location']='treasure'
        elif games[id]['players'][ids]['role']=='spy':
            games[id]['players'][ids]['items']=spyitems
            games[id]['players'][ids]['location']='spystart'
            
    for ids in games[id]['players']:
        games[id]['players'][ids]['lastloc']=games[id]['players'][ids]['location']
        sendacts(games[id]['players'][ids])
        
    t=threading.Timer(90, endturn, args=[id])
    t.start()
    games[id]['gametimer']=t
        
def endturn(id):
    texttohistory=''
    for ids in games[id]['players']:
        games[id]['texttohistory']+='Начальная локация игрока '+ games[id]['players'][ids]['name']+': '+loctoname(games[id]['players'][ids]['lastloc'])+'\n'
        games[id]['texttohistory']+='Конечная локация игрока '+ games[id]['players'][ids]['name']+': '+loctoname(games[id]['players'][ids]['location'])+'\n'
        if games[id]['players'][ids]['ready']==0:
            try:
              medit('Время вышло!',games[id]['players'][ids]['messagetoedit'].chat.id, games[id]['players'][ids]['messagetoedit'].message_id)
              games[id]['texttohistory']+=games[id]['players'][ids]['name']+' АФК!\n'
            except:
                 pass
            games[id]['players'][ids]['lastloc']=games[id]['players'][ids]['location']
    text=''        
    for ids in games[id]['players']:
        player=games[id]['players'][ids]
        if player['setupcamera']==1:
            player['cameras'].append(player['location'])
            games[id]['texttohistory']+='Шпион '+player['name']+' устанавливает камеру в локацию '+loctoname(player['location'])+'!\n'
        if player['role']=='security' and player['glasses']<=0 and player['location'] in games[id]['flashed']:
            player['flashed']=2    
            games[id]['texttohistory']+='Охранник '+player['name']+' был ослеплен флэшкой!\n'
            bot.send_message(player['id'],'Вы были ослеплены флэшкой! В следующий ход вы не сможете действовать.')
        if player['destroycamera']==1:
            if player['flashed']!=1:
                for idss in games[id]['players']:
                    if player['location'] in games[id]['players'][idss]['cameras']:
                        games[id]['players'][idss]['cameras'].remove(player['location'])
                        text+='Охранник уничтожил камеру шпиона в локации: '+player['location']+'!\n'
                        games[id]['texttohistory']+='Охранник '+player['name']+' уничтожил камеру в локации '+loctoname(player['location'])+'!\n'
            else:
                bot.send_message(player['id'],'Вы были ослеплены! Камеры шпионов обнаружить не удалось.')
                games[id]['texttohistory']+='Охранник '+player['name']+' был ослеплён! Ему не удалось обнаружить камеры.\n'
                                                                                                                        
                
        if player['stealing']==1:
            player['treasure']=1
            games[id]['texttohistory']+='Шпион '+player['name']+' украл сокровище!\n'
            bot.send_message(player['id'],'Вы успешно украли сокровище! Теперь выберитесь отсюда (Выход в той же локации, где вы начинали игру).')
        
        if player['role']=='security' and player['flashed']==0:
            for idss in games[id]['players']:
                if player['location']==games[id]['players'][idss]['location'] and games[id]['players'][idss]['role']!='security':
                    games[id]['players'][idss]['disarmed']=1
                    text+='Охранник нейтрализовал шпиона в локации: '+loctoname(player['location'])+'!\n'
                    games[id]['texttohistory']+='Охранник '+player['name']+' нейтрализовал шпиона в локации '+loctoname(player['location'])+'!\n'
                    bot.send_message(player['id'],'Вы нейтрализовали шпиона!')
                     
        if player['role']=='security' and player['flashed']==0 and player['lastloc']!=player['location']:
            for idss in games[id]['players']: 
                if games[id]['players'][idss]['lastloc']==player['location'] and games[id]['players'][idss]['location']==player['lastloc']:
                    text+='Шпион и охранник столкнулись в коридоре! Шпион нейтрализован!\n'
                    games[id]['texttohistory']+='Охранник '+player['name']+' нейтрализовал шпиона по пути в локацию '+loctoname(player['location'])+'!\n'
                    bot.send_message(player['id'],'Вы нейтрализовали шпиона!')
                    games[id]['players'][idss]['disarmed']=1
         
        if player['location']=='treasure':
            loclist=['rightcorridor','leftcorridor']     
        elif player['location']=='spystart':
            loclist=['rightcorridor','leftcorridor']
        elif player['location']=='leftcorridor':
            loclist=['leftpass','treasure', 'spystart']
        elif player['location']=='rightcorridor':
            loclist=['rightpass','treasure','spystart']
        elif player['location']=='leftpass':
            loclist=['leftcorridor','treasure']
        elif player['location']=='rightpass':
            loclist=['rightcorridor','treasure']
        else:
            loclist=[]
            
        locs=''
        for idss in loclist:
            locs+=loctoname(idss)+'\n'
        hearinfo='Прослушиваемые вами локации в данный момент:\n'+locs+'\n'    
        for idss in games[id]['players']:
            if games[id]['players'][idss]['location'] in loclist and \
            games[id]['players'][idss]['location']!=games[id]['players'][idss]['lastloc'] and \
            games[id]['players'][idss]['silent']!=1:
                hearinfo+='Вы слышите движение в локации: '+loctoname(games[id]['players'][idss]['location'])+'!\n'
        bot.send_message(player['id'],hearinfo)
        if player['treasure']==1 and player['disarmed']==0 and player['location']=='spystart':
            games[id]['treasurestealed']=1
                    
    if text=='':
        text='Ничего необычного...'
    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='История '+str(games[id]['turn'])+' хода', callback_data='history '+datagen(games[id],games[id]['texttohistory'])))
    bot.send_message(id, 'Ход '+str(games[id]['turn'])+'. Ситуация в здании:\n\n'+text, reply_markup=kb)
        
    endgame=0    
    spyalive=0    
    for ids in games[id]['players']:
        if games[id]['players'][ids]['disarmed']==0 and games[id]['players'][ids]['role']=='spy':
            spyalive+=1
    if spyalive<=0:
        endgame=1
        winner='security'
    if games[id]['turn']>=15:
        endgame=1
        winner='security'
    if games[id]['treasurestealed']==1:
        endgame=1
        winner='spy'
    if endgame==0:
        for ids in games[id]['players']:
            if games[id]['players'][ids]['flashed']==0:
                sendacts(games[id]['players'][ids])
            else:
                pass
        t=threading.Timer(90, endturn, args=[id])
        t.start()
        games[id]['gametimer']=t
        games[id]['turn']+=1
        games[id]['flashed']=[]
        games[id]['texttohistory']=''
        for ids in games[id]['players']:
            if games[id]['players'][ids]['flashed']==0:
              games[id]['players'][ids]['ready']=0
            games[id]['players'][ids]['stealing']=0
            if games[id]['players'][ids]['glasses']>0:
                games[id]['players'][ids]['glasses']-=1
            games[id]['players'][ids]['setupcamera']=0
            games[id]['players'][ids]['destroycamera']=0
            games[id]['players'][ids]['silent']=0
            if games[id]['players'][ids]['flashed']>0:
                games[id]['players'][ids]['flashed']-=1
    else:
        if winner=='security':
            bot.send_message(id, 'Победа охраны!')
        else:
            bot.send_message(id, 'Победа шпионов!')
        del games[id]

                   
def datagen(game,text):
    i=0
    word=''
    while i<4:
        word+=random.choice(symbollist)
        i+=1
    if word in history:
        return datagen(game,text)
    else:
        history.update({word:text})
        return word
  
                                      
                                      
                                      
                                      
def sendacts(player):  
    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Перемещение', callback_data='move'),types.InlineKeyboardButton(text='Предметы', callback_data='items'))
    if player['role']=='spy':
        kb.add(types.InlineKeyboardButton(text='Инфо с камер', callback_data='camerainfo'))
    kb.add(types.InlineKeyboardButton(text='Ожидать', callback_data='wait'))
    if player['flashed']==0:
      msg=bot.send_message(player['id'],'Выберите действие.',reply_markup=kb)
      player['messagetoedit']=msg
    else:
      player['ready']=1
               
     
               
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
  if 'history' in call.data:
    x=call.data.split(' ')
    x=x[1]
    try:
       bot.send_message(call.from_user.id,history[x])
    except:
       bot.send_message(call.message.chat.id, call.from_user.first_name+', произошла ошибка. Либо вы не написали боту в личку, либо '+
                       'история этой игры больше не доступна.')
  yes=0
  for ids in games:
    for idss in games[ids]['players']:
        if games[ids]['players'][idss]['id']==call.from_user.id and games[ids]['players'][idss]['ready']==0:
            yes=1
            player=games[ids]['players'][idss]
  if yes==1:
    kb=types.InlineKeyboardMarkup()
    if call.data=='move':
        if player['role']=='spy' and player['treasure']==0:
            textt='Украсть сокровище'
        else:
            textt='Комната с сокровищем'
        if player['location']=='spystart':
            kb.add(types.InlineKeyboardButton(text='Левый коридор', callback_data='leftcorridor'),types.InlineKeyboardButton(text='Правый корридор', callback_data='rightcorridor'))
            kb.add(types.InlineKeyboardButton(text='Левый обход', callback_data='leftpass'),types.InlineKeyboardButton(text='Правый обход', callback_data='rightpass'))
            kb.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
            
        if player['location']=='treasure':
            kb.add(types.InlineKeyboardButton(text='Левый коридор', callback_data='leftcorridor'),types.InlineKeyboardButton(text='Правый корридор', callback_data='rightcorridor'))
            kb.add(types.InlineKeyboardButton(text='Левый обход', callback_data='leftpass'),types.InlineKeyboardButton(text='Правый обход', callback_data='rightpass'))
            kb.add(types.InlineKeyboardButton(text='Светозащитная комната', callback_data='antiflashroom'))
            kb.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
            
        if player['location']=='leftcorridor':
            kb.add(types.InlineKeyboardButton(text='Левый обход', callback_data='leftpass'),types.InlineKeyboardButton(text='Старт шпионов', callback_data='spystart'))
            kb.add(types.InlineKeyboardButton(text=textt, callback_data='treasure'))
            kb.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
            
        if player['location']=='rightcorridor':
            kb.add(types.InlineKeyboardButton(text='Правый обход', callback_data='rightpass'),types.InlineKeyboardButton(text='Старт шпионов', callback_data='spystart'))
            kb.add(types.InlineKeyboardButton(text=textt, callback_data='treasure'))
            kb.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
            
        if player['location']=='rightpass':
            kb.add(types.InlineKeyboardButton(text='Левый обход', callback_data='leftpass'),types.InlineKeyboardButton(text='Старт шпионов', callback_data='spystart'))
            kb.add(types.InlineKeyboardButton(text=textt, callback_data='treasure'))
            kb.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
            
        if player['location']=='leftpass':
            kb.add(types.InlineKeyboardButton(text='Правый обход', callback_data='rightpass'),types.InlineKeyboardButton(text='Старт шпионов', callback_data='spystart'))
            kb.add(types.InlineKeyboardButton(text=textt, callback_data='treasure'))
            kb.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
            
        if player['location']=='antiflashroom':
            kb.add(types.InlineKeyboardButton(text=textt, callback_data='treasure'))
            kb.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
            
        medit('Куда вы хотите направиться?',call.message.chat.id,call.message.message_id, reply_markup=kb)
        
    elif call.data=='items':
        kb=types.InlineKeyboardMarkup()
        for ids in player['items']:
            x=itemtoname(ids)
            if x!=None:
                kb.add(types.InlineKeyboardButton(text=x, callback_data=ids))
        kb.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
        medit('Выберите предмет.', call.message.chat.id, call.message.message_id, reply_markup=kb)
        
    elif call.data=='camerainfo':
        if player['role']=='spy':
            text=''
            for ids in player['cameras']:
                if ids=='spystart':
                    text+='Старт шпионов:\n'
                elif ids=='treasure':
                    text+='Комната с сокровищем:\n'
                elif ids=='leftcorridor':
                    text+='Левый коридор:\n'
                elif ids=='rightcorridor':
                    text+='Правый коридор:\n'
                elif ids=='leftpass':
                    text+='Левый обход:\n'
                elif ids=='rightpass':
                    text+='Правый обход:\n'
                for idss in games[player['chatid']]['players']:
                    if games[player['chatid']]['players'][idss]['location']==ids and games[player['chatid']]['players'][idss]['id']!=player['id']:
                        text+=games[player['chatid']]['players'][idss]['name']+' был замечен на камерах!\n'
            if text=='':
                text='У вас не установлено ни одной камеры!'
            bot.answer_callback_query(call.id,text, show_alert=True)
            
    elif call.data=='wait':
        player['ready']=1
        medit('Вы пропускаете ход. Ожидайте следующего хода...',call.message.chat.id, call.message.message_id)
        player['lastloc']=player['location']
        testturn(player['chatid'])
        
    elif call.data=='leftcorridor':
        x=player['location']
        if x=='leftpass' or x=='spystart' or x=='treasure':
            player['lastloc']=player['location']
            medit('Вы перемещаетесь в локацию: '+loctoname(call.data)+'.',call.message.chat.id, call.message.message_id)
            player['location']=call.data
            player['ready']=1
            testturn(player['chatid'])
            
    elif call.data=='rightcorridor':
        x=player['location']
        if x=='rightpass' or x=='spystart' or x=='treasure':
            player['lastloc']=player['location']
            medit('Вы перемещаетесь в локацию: '+loctoname(call.data)+'.',call.message.chat.id, call.message.message_id)
            player['location']=call.data   
            player['ready']=1
            testturn(player['chatid'])
            
    elif call.data=='rightpass':
        x=player['location']
        if x=='rightcorridor' or x=='spystart' or x=='treasure':
            player['lastloc']=player['location']
            medit('Вы перемещаетесь в локацию: '+loctoname(call.data)+'.',call.message.chat.id, call.message.message_id)
            player['location']=call.data   
            player['ready']=1
            testturn(player['chatid'])
           
    elif call.data=='leftpass':
        x=player['location']
        if x=='leftcorridor' or x=='spystart' or x=='treasure':
            player['lastloc']=player['location']
            medit('Вы перемещаетесь в локацию: '+loctoname(call.data)+'.',call.message.chat.id, call.message.message_id)
            player['location']=call.data   
            player['ready']=1        
            testturn(player['chatid'])
            
    elif call.data=='treasure':
        x=player['location']
        if x!='spystart':
            if player['role']=='security':
                player['lastloc']=player['location']
                medit('Вы перемещаетесь в локацию: '+loctoname(call.data)+'.',call.message.chat.id, call.message.message_id)
                player['location']=call.data   
                player['ready']=1
            elif player['role']=='spy':
                player['lastloc']=player['location']
                medit('Вы пытаетесь украсть сокровище...',call.message.chat.id, call.message.message_id)
                player['ready']=1
                player['location']=call.data   
                player['stealing']=1
            testturn(player['chatid'])
                
    elif call.data=='antiflashroom':
        x=player['location']
        if x=='treasure':
            player['lastloc']=player['location']
            medit('Вы перемещаетесь в локацию: '+loctoname(call.data)+'.',call.message.chat.id, call.message.message_id)
            player['location']=call.data   
            player['ready']=1
            testturn(player['chatid'])
            
    elif call.data=='spystart':
        x=player['location']
        if x=='leftcorridor' or x=='rightcorridor' or x=='leftpass' or x=='rightpass':
            player['lastloc']=player['location']
            medit('Вы перемещаетесь в локацию: '+loctoname(call.data)+'.',call.message.chat.id, call.message.message_id)
            player['location']=call.data
            player['ready']=1
            testturn(player['chatid'])
            
    elif call.data=='glasses':
        if 'glasses' in player['items']:
            player['items'].remove('glasses')
            player['glasses']=1
            bot.answer_callback_query(call.id,'Вы успешно надели очки! На этот ход вы защищены от флэшек!')
            kb=types.InlineKeyboardMarkup()
            for ids in player['items']:
                x=itemtoname(ids)
                if x!=None:
                    kb.add(types.InlineKeyboardButton(text=x, callback_data=ids))
            kb.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
            medit('Выберите предмет.', call.message.chat.id, call.message.message_id, reply_markup=kb)
            
    elif call.data=='pistol':
        if 'pistol' in player['items']:
            player['destroycamera']=1
            player['ready']=1
            testturn(player['chatid'])
            medit('Выбрано действие: уничтожение вражеских камер.', call.message.chat.id, call.message.message_id)
            
    elif call.data=='camera':
        if 'camera' in player['items']:
            player['items'].remove('camera')
            player['setupcamera']=1
            player['ready']=1
            testturn(player['chatid'])
            medit('Выбрано действие: установка камеры.', call.message.chat.id, call.message.message_id)
            
    elif call.data=='flash':
        if 'flash' in player['items']:
            kb=types.InlineKeyboardMarkup()
            if player['location']=='leftcorridor':
                locs=['spystart','treasure', 'leftpass']
            if player['location']=='rightcorridor':
                locs=['spystart','treasure', 'rightpass']
            if player['location']=='rightpass':
                locs=['treasure', 'rightcorridor']
            if player['location']=='leftpass':
                locs=['treasure', 'leftcorridor']
            if player['location']=='treasure':
                locs=['leftpass','rightpass','leftcorridor','rightcorridor']
            if player['location']=='spystart':
                locs=['leftcorridor','rightcorridor']
            for ids in locs:
                kb.add(types.InlineKeyboardButton(text=loctoname(ids), callback_data='flash '+ids))
            kb.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
            medit('Выберите, куда будете кидать флэшку.', call.message.chat.id, call.message.message_id, reply_markup=kb)
            
    elif 'flash' in call.data:
      print (call.data)
      if 'flash' in player['items']:
        kb=types.InlineKeyboardMarkup()
        x=call.data.split(' ')
        location=x[1]
        print(location)
        player['items'].remove('flash')
        games[player['chatid']]['flashed'].append(location)
        medit('Вы бросили флэшку в локацию: '+loctoname(location)+'.', call.message.chat.id, call.message.message_id)
        games[player['chatid']]['texttohistory']+='Шпион '+player['name']+' бросил флэшку в локацию '+loctoname(location)+'!\n'
        kb.add(types.InlineKeyboardButton(text='Перемещение', callback_data='move'),types.InlineKeyboardButton(text='Предметы', callback_data='items'))
        if player['role']=='spy':
                kb.add(types.InlineKeyboardButton(text='Инфо с камер', callback_data='camerainfo'))
        kb.add(types.InlineKeyboardButton(text='Ожидать', callback_data='wait'))
        msg=bot.send_message(player['id'],'Выберите действие.', reply_markup=kb)
        player['currentmessage']=msg
        player['messagetoedit']=msg
        
    elif call.data=='costume':
        if 'costume' in player['items']:
            kb=types.InlineKeyboardMarkup()
            player['items'].remove('costume')
            player['silent']=1
            games[player['chatid']]['texttohistory']+='Шпион '+player['name']+' надел маскировочный костюм!\n'
            medit('Вы надели маскировочный костюм! На этом ходу ваши передвижения не будут услышаны.', call.message.chat.id, call.message.message_id)
            kb.add(types.InlineKeyboardButton(text='Перемещение', callback_data='move'),types.InlineKeyboardButton(text='Предметы', callback_data='items'))
            if player['role']=='spy':
                kb.add(types.InlineKeyboardButton(text='Инфо с камер', callback_data='camerainfo'))
            kb.add(types.InlineKeyboardButton(text='Ожидать', callback_data='wait'))
            msg=bot.send_message(player['id'],'Выберите действие.', reply_markup=kb)
            player['currentmessage']=msg
            player['messagetoedit']=msg
            
    elif call.data=='back':
        kb=types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Перемещение', callback_data='move'),types.InlineKeyboardButton(text='Предметы', callback_data='items'))
        if player['role']=='spy':
            kb.add(types.InlineKeyboardButton(text='Инфо с камер', callback_data='camerainfo'))
        kb.add(types.InlineKeyboardButton(text='Ожидать', callback_data='wait'))
        medit('Выберите действие.', call.message.chat.id, call.message.message_id, reply_markup=kb)
        

            
            
            
            
def loctoname(x):
    if x=='leftcorridor':
        return 'Левый коридор'
    if x=='rightcorridor':
        return 'Правый коридор'
    if x=='spystart':
        return 'Старт шпионов'
    if x=='treasure':
        return 'Комната с сокровищем'
    if x=='leftcorridor':
        return 'Левый коридор'
    if x=='leftpass':
        return 'Левый обход'
    if x=='rightpass':
        return 'Правый обход'
    if x=='antiflashroom':
        return 'Светозащитная комната'
            
def itemtoname(x):
    if x=='flash':
        return 'Флэшка'
    elif x=='costume':
        return 'Маскировочный костюм'
    elif x=='glasses':
        return 'Защитные очки'
    elif x=='pistol':
        return 'Пистолет'
    elif x=='camera':
        return 'Камера'
    else:
        return None
        
        

            
            
def creategame(id):
    return{id:{
        'chatid':id,
        'players':{},
        'turn':1,
        'spies':0,
        'security':0,
        'timer':None,
        'locs':['treasure','spystart','leftcorridor','rightcorridor','leftpass','rightpass','antiflashroom'],
        'flashed':[],
        'treasurestealed':0,
        'gametimer':None,
        'started':0,
        'texttohistory':''
          }
     }
    

def createplayer(id,name,chatid):
    return{id:{
        'id':id,
        'name':name,
        'location':None,
        'team':None,
        'items':[],
        'ready':0,
        'messagetoedit':None,
        'cameras':[],
        'chatid':chatid,
        'stealing':0,
        'glasses':0,
        'setupcamera':0,
        'destroycamera':0,
        'currentmessage':None,
        'silent':0,
        'flashed':0,
        'lastloc':None,
        'treasure':0,
        'disarmed':0
          }
    }



if True:
   print('7777')
   bot.polling(none_stop=True,timeout=600)

