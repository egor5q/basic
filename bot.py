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

games={}


ban=[]
timers={}



@bot.message_handler(commands=['stopspam'])
def spammm(m):
      if m.from_user.id==441399484:
           try:
             print(str(m.chat.id))
             bot.pin_chat_message(m.chat.id, m.message_id, disable_notification=True)
           except:
             print('except')

client1=os.environ['database']
client=MongoClient(client1)
db=client.minigame
users=db.users
chats=db.chats
guess=db.guessusergame
guessrecs=db.guessrecords
pokemonss=db.pokemons

rolelist=['wolf', 'gunner', 'mage', 'nindza', 'cat', 'killer', 'bear']

symbollist=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
           'а','б','в','г','д','е','ё','ж','з','и','й','к','л','м','н','о','п','р','с','т','у','ф','х','ц','ч','ш','щ','ъ','ы','ь','э','ю','я',
           '1','2','3','4','5','6','7','8','9','0']


def medit(message_text,chat_id, message_id,reply_markup=None,parse_mode='Markdown'):
    return bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=message_text,reply_markup=reply_markup,
                                 parse_mode=parse_mode)


pokemons=['Дилдак','Лошод','Пенис','Залупер']

def dailypoke(id):
      x=random.randint(1200,4500)
      t=threading.Timer(x, dailypoke, args=[id])
      t.start()
      gold=random.randint(1,100)
      if gold==1:
            gold='*золотой* '
      else:
            gold=''
      poke=random.choice(pokemons)
      kb=types.InlineKeyboardMarkup()
      kb.add(types.InlineKeyboardButton(text='Поймать', callback_data=poke)
      bot.send_message(id, 'Обнаружен '+gold+'покемон '+poke+'! Жмите кнопку ниже, чтобы попытаться поймать.', parse_mode='markdown')


           
@bot.callback_query_handler(func=lambda call:True)
def inline(call):
    givepoke(call.data, call.chat.id, call.message.message_id, call.from_user.id)
             
   
def givepoke(pokemon,id, mid, name):
             medit('Покемона поймал '+name+'!',id, mid)
             
 
@bot.message_handler(content_types=['text'])
def textt(m):
    x=chats.find_one({'id':m.chat.id})
    if x==None:
        chats.insert_one(createchat(m.chat.id))
    if users.find_one({'id':m.from_user.id})!=None:
           users.update_one({'id':m.from_user.id}, {'$set':{'nameofuser':m.from_user.first_name}})

            
      
  
  
if True:
 try:
   print('7777')
   dailypoke(-1001256539790)
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
       
