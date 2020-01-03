import random
import traceback
from telebot import types, TeleBot
import time
import threading
import config
import telebot
import os
import config

bot = TeleBot(os.environ['botname'])

client=MongoClient(os.environ['database'])
db=client.
users=db.users

games = {}

def createplayer(user):
    return {user.id:{
        'id':user.id,
        'name':user.first_name
    }
           }

def createuser(user):
  return {
    'id':user.id,
    'name':user.first_name
  }


@bot.message_handler(commands=['start'])
def start(m):
    user = users.find_one({'id':m.from_user.id})
    if user == None:
        user = users.insert_one(createuser(m.from_user))
        user = users.find_one({'id':m.from_user.id})
    bot.send_message(m.chat.id, 'Приветствие')
    
    
@bot.message_handler(commands=['me'])
def mee(m):
    user = users.find_one({'id':m.from_user.id})
    if user == None:
        user = users.insert_one(createuser(m.from_user))
        user = users.find_one({'id':m.from_user.id})
    text = 'Ваш профиль:\n'
    bot.send_message(m.chat.id, text)
    
        

    
@bot.message_handler(commands=['startgame'])
def startgame(m):
    user = users.find_one({'id':m.from_user.id})
    if user == None:
        user = users.insert_one(createuser(m.from_user))
        user = users.find_one({'id':m.from_user.id})
    if m.chat.id not in games:
        game = creategame(m)
        x = m.text.split(' ')

        games.update(game)
        game = games[m.chat.id]
        bot.send_message(m.chat.id, 'Подготовка к игре запущена.', parse_mode = 'markdown')
    else:
        bot.send_message(m.chat.id, 'В этом чате уже есть игра!')
        return
    
    
@bot.message_handler(commands=['go'])
def go(m):
    if m.chat.id not in games:
        bot.send_message(m.chat.id, 'Игра ещё не была создана!')
        return
    game = games[m.chat.id]
    if game['started'] == False:
        game['started'] = True

        bot.send_message(m.chat.id, 'Игра начинается!')
        msg = bot.send_message(m.chat.id, 'Start.')
        game['msg'] = msg
        threading.Timer(5, next_turn, args=[game]).start()
        
     
def creategame(m):
    return {m.chat.id:{
      'id':m.chat.id,
      'players':{},
      'msg':None,
      'turn':1,
      'text':''
        
    }
           }
    
    
    
def medit(message_text, chat_id, message_id, reply_markup=None, parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message_text,
                                    reply_markup=reply_markup,
                                    parse_mode=parse_mode)

