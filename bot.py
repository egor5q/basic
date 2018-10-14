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


nearlocs={'spystart':['leftcorridor','rightcorridor','midcorridor'],
          'leftcorridor':['spystart','treasure','leftpass'],
          'rightcorridor':['spystart','treasure', 'rightpass'],
          'rightpass':['rightcorridor','stock'],
          'leftpass':['stock','leftcorridor'],
          'treasure':['leftcorridor','rightcorridor','stock','midcorridor'],
          'spystart':['leftcorridor','rightcorridor','midcorridor'],
          'midcorridor':['spystart','treasure'],
          'stock':['rightpass','leftpass','treasure']
}


@bot.message_handler(commands=['creategame'])
def creategamee(m):
    if m.chat.id not in games:
        games.update(creategame(m.chat.id))
        bot.send_message(m.chat.id, 'Жмите /join, чтобы присоединиться! До отмены игры 5 минут.')
        t=threading.Timer(300,cancelgame,args=[m.chat.id])
        t.start()
        games[m.chat.id]['timer']=t
        
     
@bot.message_handler(commands=['map'])
def map(m):
    bot.send_photo(m.chat.id, 'AgADAgAD06sxG7wwGEqukXmiDU8iF5zPtw4ABCn0Y60xUVfWDfgEAAEC')

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
    if no==0 and len(games[m.chat.id]['players'])<2:
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
    securityitems=['glasses','pistol','tizer', 'glasses','shockmine']
    spyitems=['camera','camera','camera','flash','costume', 'flash','mineremover']
    for ids in games[id]['players']:
        if games[id]['spies']>games[id]['security']:
            games[id]['players'][ids]['role']='security'
            games[id]['security']+=1
            bot.send_message(games[id]['players'][ids]['id'], 'Вы - охранник! Ваша цель - не дать шпионам украсть сокровище!'+\
                             'Если продержитесь 25 ходов - вам на помощь приедет спецназ, и вы победите!')
        elif games[id]['spies']<games[id]['security']:
            games[id]['players'][ids]['role']='spy'
            games[id]['spies']+=1
            bot.send_message(games[id]['players'][ids]['id'], 'Вы - шпион! Ваша цель - украсть сокровище!'+\
                             'Не попадитесь на глаза охраннику и сделайте всё меньше, чем за 26 ходов, иначе проиграете!')
        elif games[id]['spies']==games[id]['security']:
            x=random.choice(['spy','security'])
            games[id]['players'][ids]['role']=x
            if x=='spy':
                games[id]['spies']+=1
                bot.send_message(games[id]['players'][ids]['id'], 'Вы - шпион! Ваша цель - украсть сокровище!'+\
                             'Не попадитесь на глаза охраннику и сделайте всё меньше, чем за 26 ходов, иначе проиграете!')
            elif x=='security':
                games[id]['security']+=1
                bot.send_message(games[id]['players'][ids]['id'], 'Вы - охранник! Ваша цель - не дать шпионам украсть сокровище!'+\
                             'Если продержитесь 25 ходов - вам на помощь приедет спецназ, и вы победите!')
                
    for ids in games[id]['players']:
        if games[id]['players'][ids]['role']=='security':
            games[id]['players'][ids]['items']=securityitems
            games[id]['players'][ids]['location']='stock'
        elif games[id]['players'][ids]['role']=='spy':
            games[id]['players'][ids]['items']=spyitems
            games[id]['players'][ids]['location']='spystart'
            
    for ids in games[id]['players']:
        games[id]['players'][ids]['lastloc']=games[id]['players'][ids]['location']
        sendacts(games[id]['players'][ids])
    bot.send_message(id, 'Игра начинается! Охранники, шпионы - по позициям!')
        
    t=threading.Timer(90, endturn, args=[id])
    t.start()
    games[id]['gametimer']=t
        
def endturn(id):
    texttohistory=''
    for ids in games[id]['players']:
        if games[id]['players'][ids]['role']=='spy':
            g='шпиона'
        else:
            g='охранника'
        games[id]['texttohistory']+='Начальная локация '+g+' '+games[id]['players'][ids]['name']+': '+loctoname(games[id]['players'][ids]['lastloc'])+'\n\n'
        games[id]['texttohistory']+='Конечная локация '+g+' '+games[id]['players'][ids]['name']+': '+loctoname(games[id]['players'][ids]['location'])+'\n\n'
        if games[id]['players'][ids]['ready']==0:
            try:
              medit('Время вышло!',games[id]['players'][ids]['messagetoedit'].chat.id, games[id]['players'][ids]['messagetoedit'].message_id)
              games[id]['texttohistory']+=games[id]['players'][ids]['name']+' АФК!\n\n'
            except:
                 pass
            games[id]['players'][ids]['lastloc']=games[id]['players'][ids]['location']
    for ids in games[id]['players']:
        if games[id]['players'][ids]['moving']==0:
            games[id]['players'][ids]['lastloc']=games[id]['players'][ids]['location']
    text=''        
    for ids in games[id]['players']:
        player=games[id]['players'][ids]
        if player['setupcamera']==1:
            player['cameras'].append(player['location'])
            games[id]['texttohistory']+='Шпион '+player['name']+' устанавливает камеру в локацию '+loctoname(player['location'])+'!\n\n'
        if player['role']=='security' and player['glasses']<=0 and player['location'] in games[id]['flashed']:
            player['flashed']=1  
            games[id]['texttohistory']+='Охранник '+player['name']+' был ослеплен флэшкой!\n\n'
            bot.send_message(player['id'],'Вы были ослеплены флэшкой! В следующий ход вы не сможете действовать.')
        if player['role']=='spy' and player['location'] in games[id]['shockminelocs']:
          if player['removemine']==0:
            player['shocked']=1
            games[id]['texttohistory']+='Шпион '+player['name']+' наступил на мину-шокер в локации '+loctoname(player['location'])+'!\n\n'
            bot.send_message(player['id'],'Вы наступили на мину-шокер! В следующий ход вы не сможете действовать.')
          else:
            games[id]['texttohistory']+='Шпион '+player['name']+' обезвредил мину-шокер в локации '+loctoname(player['location'])+'!\n\n'
            bot.send_message(player['id'],'Вы обезвредили мину-шокер!')
          try:
              games[id]['shockminelocs'].remove(player['location'])
          except:
              pass
            
        if player['destroycamera']==1:
            if player['flashed']!=1:
                for idss in games[id]['players']:
                    if player['location'] in games[id]['players'][idss]['cameras']:
                        games[id]['players'][idss]['cameras'].remove(player['location'])
                        text+='Охранник уничтожил камеру шпиона в локации: '+player['location']+'!\n'
                        games[id]['texttohistory']+='Охранник '+player['name']+' уничтожил камеру в локации '+loctoname(player['location'])+'!\n\n'
            else:
                bot.send_message(player['id'],'Вы были ослеплены! Камеры шпионов обнаружить не удалось.')
                games[id]['texttohistory']+='Охранник '+player['name']+' был ослеплён! Ему не удалось обнаружить камеры.\n\n'
                                                                                                                        
                
        if player['stealing']==1:
            player['treasure']=1
            games[id]['texttohistory']+='Шпион '+player['name']+' украл сокровище!\n\n'
            bot.send_message(player['id'],'Вы успешно украли сокровище! Теперь выберитесь отсюда (Выход в той же локации, где вы начинали игру).')
        
        if player['role']=='security':
            for idss in games[id]['players']:
                if player['location']==games[id]['players'][idss]['location'] and games[id]['players'][idss]['role']!='security':
                  if player['flashed']==0:
                    games[id]['players'][idss]['disarmed']=1
                    text+='Охранник нейтрализовал шпиона в локации: '+loctoname(player['location'])+'!\n'
                    games[id]['texttohistory']+='Охранник '+player['name']+' нейтрализовал шпиона в локации '+loctoname(player['location'])+'!\n\n'
                    bot.send_message(player['id'],'Вы нейтрализовали шпиона!')
                  else:
                    bot.send_message(games[id]['players'][idss]['id'], 'В вашей текущей локации вы видите ослеплённого охранника! Поторопитесь уйти...') 
                     
        if player['role']=='security' and player['flashed']==0 and player['lastloc']!=player['location']:
            for idss in games[id]['players']: 
                if games[id]['players'][idss]['lastloc']==player['location'] and games[id]['players'][idss]['location']==player['lastloc']:
                    text+='Шпион и охранник столкнулись в коридоре! Шпион нейтрализован!\n'
                    games[id]['texttohistory']+='Охранник '+player['name']+' нейтрализовал шпиона по пути в локацию '+loctoname(player['location'])+'!\n\n'
                    bot.send_message(player['id'],'Вы нейтрализовали шпиона!')
                    games[id]['players'][idss]['disarmed']=1
        
        loclist=[]
        for idss in nearlocs[player['location']]:
            loclist.append(idss)
        loclist.append(player['location'])
            
        locs=''
        for idss in loclist:
            if idss!=player['location']:
                locs+=loctoname(idss)+'\n'
        hearinfo='Прослушиваемые вами локации в данный момент:\n'+locs+'\n' 
        for idss in games[id]['players']:
            if games[id]['players'][idss]['location'] in loclist and \
            games[id]['players'][idss]['location']!=games[id]['players'][idss]['lastloc'] and \
            games[id]['players'][idss]['silent']!=1 and player['id']!=games[id]['players'][idss]['id']:
                if games[id]['players'][idss]['location']!=player['location']:
                    hearinfo+='Вы слышите движение в локации: '+loctoname(games[id]['players'][idss]['location'])+'!\n'
                else:
                    hearinfo+='Вы слышите движение в вашей текущей локации!!\n'
                    
        bot.send_message(player['id'],hearinfo)
    for ids in games[id]['players']:
        if games[id]['players'][ids]['treasure']==1 and \
        games[id]['players'][ids]['disarmed']==0 and \
        games[id]['players'][ids]['location']=='spystart':
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
    if games[id]['turn']>=25:
        endgame=1
        winner='security'
        games[id]['texttohistory']+='Победа охраны по причине: прошло 25 ходов!\n\n'
    if games[id]['treasurestealed']==1:
        endgame=1
        winner='spy'
    if endgame==0:
        for ids in games[id]['players']:
            if games[id]['players'][ids]['flashed']==0 and games[id]['players'][ids]['shocked']==0:
                sendacts(games[id]['players'][ids])
            else:
                games[id]['players'][ids]['lastloc']=games[id]['players'][ids]['location']
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
            games[id]['players'][ids]['moving']=0
            games[id]['players'][ids]['destroycamera']=0
            games[id]['players'][ids]['silent']=0
            if games[id]['players'][ids]['flashed']>0:
                games[id]['players'][ids]['flashed']-=1
            if games[id]['players'][ids]['shocked']>0:
                games[id]['players'][ids]['shocked']-=1
            games[id]['players'][ids]['removemine']=0
    else:
        if winner=='security':
            bot.send_message(id, 'Победа охраны!')
        else:
            bot.send_message(id, 'Победа шпионов!')
        try:
            del games[id]
        except:
            pass

                   
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
    if player['role']=='security':
        kb.add(types.InlineKeyboardButton(text='Камера в сокровищнице', callback_data='treasureinfo'))
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
    yes=0
    for ids in games:
        for idss in games[ids]['players']:
            if games[ids]['players'][idss]['id']==call.from_user.id:
                yes=1
    if yes==0:
      try:
         print(history)
         print(x)
         aa=history[x]
         try:
             bot.send_message(call.from_user.id,history[x])
         except:
             bot.send_message(call.message.chat.id, call.from_user.first_name+', напишите боту в личку, чтобы я мог отправлять вам историю боя!')
      except:
         medit('История этой игры больше недоступна!',call.message.chat.id,call.message.message_id)
    else:
        bot.send_message(call.message.chat.id, call.from_user.first_name+', нельзя смотреть историю, находясь в игре!')
        
  yes=0
  for ids in games:
    for idss in games[ids]['players']:
        if games[ids]['players'][idss]['id']==call.from_user.id and games[ids]['players'][idss]['ready']==0:
            yes=1
            player=games[ids]['players'][idss]
  if yes==1:
    kb=types.InlineKeyboardMarkup()
    if call.data=='move':
        for ids in nearlocs[player['location']]:
            kb.add(types.InlineKeyboardButton(text=loctoname(ids), callback_data='move '+ids))
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
                text+=loctoname(ids)+':\n'
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
        
    elif call.data=='mineremover':
        if 'mineremover' in player['items']:
            kb=types.InlineKeyboardMarkup()
            player['items'].remove('mineremover')
            player['removemine']=1
            games[player['chatid']]['texttohistory']+='Шпион '+player['name']+' готовится обезвреживать мину-шокер.\n\n'
            medit('Вы готовитесь обезвредить мину-шокер в своей следующей локации.', call.message.chat.id, call.message.message_id)
            kb=types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(text='Перемещение', callback_data='move'),types.InlineKeyboardButton(text='Предметы', callback_data='items'))
            if player['role']=='spy':
                kb.add(types.InlineKeyboardButton(text='Инфо с камер', callback_data='camerainfo'))
            if player['role']=='security':
                kb.add(types.InlineKeyboardButton(text='Камера в сокровищнице', callback_data='treasureinfo'))
            kb.add(types.InlineKeyboardButton(text='Ожидать', callback_data='wait'))
            msg=bot.send_message(player['id'],'Выберите действие.', reply_markup=kb)
            player['currentmessage']=msg
            player['messagetoedit']=msg     
        
        
    elif 'move' in call.data:
        x=call.data.split(' ')
        x=x[1]
        if x in nearlocs[player['location']]:
            player['lastloc']=player['location']
            medit('Вы перемещаетесь в локацию: '+loctoname(x)+'.',call.message.chat.id, call.message.message_id)
            player['location']=x
            player['ready']=1
            player['moving']=1
            if player['role']=='spy' and player['location']=='treasure':
                player['stealing']=1
            testturn(player['chatid'])
            
            
    elif call.data=='glasses':
        if 'glasses' in player['items']:
            player['items'].remove('glasses')
            player['glasses']=1
            games[player['chatid']]['texttohistory']+='Охранник '+player['name']+' надел очко!\n\n'
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
            player['lastloc']=player['location']
            testturn(player['chatid'])
            medit('Выбрано действие: установка камеры.', call.message.chat.id, call.message.message_id)
            
    elif call.data=='flash':
        if 'flash' in player['items']:
            locs=[]
            for ids in nearlocs[player['location']]:
                locs.append(ids)
            locs.append(player['location'])
            for ids in locs:
                if ids!=player['location']:
                    kb.add(types.InlineKeyboardButton(text=loctoname(ids), callback_data='flash '+ids))
                else:
                    kb.add(types.InlineKeyboardButton(text='Эта локация', callback_data='flash '+ids))
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
        games[player['chatid']]['texttohistory']+='Шпион '+player['name']+' бросил флэшку в локацию '+loctoname(location)+'!\n\n'
        kb.add(types.InlineKeyboardButton(text='Перемещение', callback_data='move'),types.InlineKeyboardButton(text='Предметы', callback_data='items'))
        if player['role']=='spy':
                kb.add(types.InlineKeyboardButton(text='Инфо с камер', callback_data='camerainfo'))
        if player['role']=='security':
            kb.add(types.InlineKeyboardButton(text='Камера в сокровищнице', callback_data='treasureinfo'))
        kb.add(types.InlineKeyboardButton(text='Ожидать', callback_data='wait'))
        msg=bot.send_message(player['id'],'Выберите действие.', reply_markup=kb)
        player['currentmessage']=msg
        player['messagetoedit']=msg
        
    elif call.data=='costume':
        if 'costume' in player['items']:
            kb=types.InlineKeyboardMarkup()
            player['items'].remove('costume')
            player['silent']=1
            games[player['chatid']]['texttohistory']+='Шпион '+player['name']+' надел маскировочный костюм!\n\n'
            medit('Вы надели маскировочный костюм! На этом ходу ваши передвижения не будут услышаны.', call.message.chat.id, call.message.message_id)
            kb.add(types.InlineKeyboardButton(text='Перемещение', callback_data='move'),types.InlineKeyboardButton(text='Предметы', callback_data='items'))
            if player['role']=='spy':
                kb.add(types.InlineKeyboardButton(text='Инфо с камер', callback_data='camerainfo'))
            if player['role']=='security':
                kb.add(types.InlineKeyboardButton(text='Камера в сокровищнице', callback_data='treasureinfo'))
            kb.add(types.InlineKeyboardButton(text='Ожидать', callback_data='wait'))
            msg=bot.send_message(player['id'],'Выберите действие.', reply_markup=kb)
            player['currentmessage']=msg
            player['messagetoedit']=msg
        
    elif call.data=='shockmine':
        if 'shockmine' in player['items']:
            kb=types.InlineKeyboardMarkup()
            player['items'].remove('shockmine')
            games[player['chatid']]['texttohistory']+='Охранник '+player['name']+' установил мину-шокер в локации '+loctoname(player['location'])+'!\n\n'
            medit('Вы устанавливаете мину-шокер.', call.message.chat.id, call.message.message_id)
            player['ready']=1
            game[player['chatid']]['shockminelocs'].append(player['location'])
            
    elif call.data=='back':
        kb=types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Перемещение', callback_data='move'),types.InlineKeyboardButton(text='Предметы', callback_data='items'))
        if player['role']=='spy':
            kb.add(types.InlineKeyboardButton(text='Инфо с камер', callback_data='camerainfo'))
        if player['role']=='security':
            kb.add(types.InlineKeyboardButton(text='Камера в сокровищнице', callback_data='treasureinfo'))
        kb.add(types.InlineKeyboardButton(text='Ожидать', callback_data='wait'))
        medit('Выберите действие.', call.message.chat.id, call.message.message_id, reply_markup=kb)
        
    elif call.data=='treasureinfo':
        stealed=0
        text='Сокровищница:\n'
        for idss in games[player['chatid']]['players']:
            if games[player['chatid']]['players'][idss]['treasure']==1:
                stealed=1
            if games[player['chatid']]['players'][idss]['location']=='treasure' and games[player['chatid']]['players'][idss]['id']!=player['id']:
                text+=games[player['chatid']]['players'][idss]['name']+' был замечен на камере!\n'
        if stealed==1:
            text+='В комнате нет сокровища!!!'
        else:
            text+='Сокровище на месте.'
        bot.answer_callback_query(call.id,text, show_alert=True)         
            
            
            
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
    if x=='midcorridor':
        return 'Центральный корридор'
    if x=='stock':
        return 'Склад'
            
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
    elif x=='shockmine':
        return 'Мина-шокер'
    elif x=='mineremover':
        return 'Водяная бомба'
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
        'locs':['treasure','spystart','leftcorridor','rightcorridor','leftpass','rightpass','antiflashroom','midcorridor','stock'],
        'flashed':[],
        'treasurestealed':0,
        'gametimer':None,
        'started':0,
        'texttohistory':'',
        'shockminelocs':[]
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
        'disarmed':0,
        'moving':0,
        'shocked':0,
        'removemine':0
          }
    }


@bot.message_handler(content_types=['photo'])
def jjhgh(m):
    print(m.chat.id)
    print(m)



if True:
   print('7777')
   bot.send_message(-1001373723053, 'Бот был перезагружен!')
   bot.polling(none_stop=True,timeout=600)

