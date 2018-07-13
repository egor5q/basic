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


from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectionError


token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)
vip=[441399484, 55888804]
games={}
skills=[]

client1=os.environ['database']
client=MongoClient(client1)
db=client.minigame
users=db.users
chats=db.chats

rolelist=['wolf', 'gunner', 'berserk', 'nindza', 'cat', 'killer']

symbollist=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
           'а','б','в','г','д','е','ё','ж','з','и','й','к','л','м','н','о','п','р','с','т','у','ф','х','ц','ч','ш','щ','ъ','ы','ь','э','ю','я']


def medit(message_text,chat_id, message_id,reply_markup=None,parse_mode='Markdown'):
    return bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=message_text,reply_markup=reply_markup,
                                 parse_mode=parse_mode)



    
@bot.message_handler(commands=['start'])
def start(m):
  if users.find_one({'id':m.from_user.id})==None:
        try:
            bot.send_message(m.from_user.id, 'Вы создали персонажа! Теперь дайте ему имя командой /name.')
            users.insert_one(createuser(m.from_user.id, m.from_user.first_name))
            x=random.choice(rolelist)
            users.update_one({'id':m.from_user.id}, {'$set':{'role':x}})
            bot.send_message(m.chat.id, 'Ваша первая роль - '+roletoname(x)+'.')
        except:
            bot.send_message(m.chat.id, 'Напишите боту в личку!')

@bot.message_handler(commands=['addme'])
def addme(m):
    x=chats.find_one({'id':m.chat.id})
    if x!=None:
      y=users.find_one({'id':m.from_user.id})
      if y!=None:
       if y['name']!=None:
        if m.from_user.id not in x['users']:
            chats.update_one({'id':m.chat.id}, {'$push':{'users':m.from_user.id}})
            bot.send_message(m.chat.id, 'Теперь вы в игре!')
        else:
            bot.send_message(m.chat.id, 'Вы уже в игре!')
       else:
         bot.send_message(m.chat.id, 'Сначала дайте персонажу имя!')
      else:
        bot.send_message(m.chat.id, 'Напишите боту в личку!')


@bot.message_handler(commands=['fight'])
def fighttt(m):
    name=users.find_one({'id':m.from_user.id})
    x=m.text.split(' ')
    if name['name']!=None:
      if len(x)==2:
        y=users.find_one({'name':x[1]})
        x=users.find_one({'name':name['name']})
        z=chats.find_one({'id':m.chat.id})
        if z!=None:
          if x!=None and y!=None:
            if x['id'] in z['users'] and y['id'] in z['users']:
                pass
            else:
                x=None
                y=None
          else:
            bot.send_message(m.chat.id, 'Такого юзера не существует в данном чате!')
        if y!=None and x!=None:
            fight(x, y, m.chat.id)
        else:
            bot.send_message(m.chat.id, 'Такого юзера не существует в данном чате!')
      else:
           bot.send_message(m.chat.id, 'Используйте формат:\n/fight *имя_бойца*', parse_mode='markdown')
    else:
           bot.send_message(m.chat.id, 'Сначала дайте персонажу имя! (/name)')
            
            
@bot.message_handler(commands=['users'])
def userssss(m):
    x=chats.find_one({'id':m.chat.id})
    if x!=None:
           text=''
           y=users.find({})
           for ids in y:
                if ids['id'] in x['users']:
                     text+='`'+ids['name']+'`'+'\n'
           if text=='':
              text='В данном чате нет ни одного зарегистрировавшегося юзера.'
           bot.send_message(m.chat.id, text, parse_mode='markdown')
    else:
        bot.send_message(m.chat.id, 'В данном чате не было отправлено ни одного сообщения!')
        

def roletoname(x):
    role='У роли нет названия, пишите @Loshadkin'
    if x=='wolf':
        role='Волк'
    if x=='gunner':
        role='Стрелок'
    if x=='berserk':
        role='Берсерк'
    if x=='nindza':
        role='Ниндзя'
    if x=='cat':
        x='Кот'
    if x=='killer':
        role='Убийца'
    return role

def fight(x,y, id):
    if x['id']!=y['id']:
        pass
    else:
        bot.send_message(id, 'Нельзя сражаться с самим собой!')


@bot.message_handler(commands=['name'])
def name(m):
    text=m.text.split(' ')
    if len(text)==2:
        if len(text[1])<=25:
          i=0
          for symbol in text[1]:
            if symbol not in symbollist:
                i=1
          if i==0:
            zz=users.find({})
            spisok=[]
            for ids in zz:
                spisok.append(ids['name'])
            if text[1] not in spisok:
                x=users.find_one({'id':m.from_user.id})
                users.update_one({'id':m.from_user.id}, {'$set':{'name':text[1]}})
                bot.send_message(m.chat.id, 'Вы успешно изменили имя на '+text[1]+'!')
            else:
                bot.send_message(m.chat.id, 'Такое имя уже занято!')
          else:
            bot.send_message(m.chat.id, 'В нике можно использовать только русские и английские символы!')
        else:
            bot.send_message(m.chat.id, 'Длина ника не должна превышать 25 символов!')
    else:
       bot.send_message(m.chat.id, 'Для переименования используйте формат:\n/name *имя*, где *имя* - имя вашего персонажа.', parse_mode='markdown')


def createchat(id):
    return{'id':id,
           'users':[]
          }
    
    
def createuser(id, name):
    return{'id':id,
           'nameofuser':name,
           'name':None,
           'role':None,
           'dies':0,
           'wins':0,
           'looses':0,
           'games':0
          }

@bot.message_handler(content_types=['text'])
def textt(m):
    x=chats.find_one({'id':m.chat.id})
    if x==None:
        chats.insert_one(createchat(m.chat.id))
  
  
if True:
 try:
   print('7777')
   bot.polling(none_stop=True,timeout=600)
 except (requests.ReadTimeout):
        print('!!! READTIME OUT !!!')           
        bot.stop_polling()
        time.sleep(1)
        check = True
        while check==True:
          try:
            bot.polling(none_stop=True,timeout=1)
            print('checkkk')
            check = False
          except (requests.exceptions.ConnectionError):
            time.sleep(1)
   
#if __name__ == '__main__':
 # bot.polling(none_stop=True)

#while True:
#    try:
  #      bot.polling()
 #   except:
  #      pass
#    time.sleep(0.1)
       
