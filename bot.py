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


pokeban=[]

pokemons=['Подрочу','Дрочемыш','Хуебес','Писькозавр','Кончефлыга','Блядун','Хуйдрочу','Подрочилла','Дрочь','Залупяндрий','Еблодок',
          'Спермобак','Слоудроч','Пиздераст','Спермон','Кулдыга','Покесперм','Спермомон','Спермак', 'Подрочиха','Уебаныш','Хуйсосалкин',
         'Говнюк','Уебак','Писюк', 'Подзалупыш', 'Хуй','Долбоёбыч', 'Хуйкинс', 'Отсосалкин', 'Вспермеротыч','Анальныйконь','Има','Обосратыш','Ебиська',
         'Пездюк','Пидрила ебаная', 'Хуй моржовый', 'Стоякомон', 'Кремнехуй','Стояк','Траходром','Дрочик','Конский хуй','Натуралмон',
         'Геймон','Потрахун', 'Ебусобак','Исма','Кроссфакчу','Вжопухочу','Инцестер','Ебало','Рэд пидорас','Люблюхуймон','Вжопумон',
         'Виномон (Винко гей)','Подзалупка','Аналыч','Пидрохуй','Объебаныч','Говнарь','Гнида','Пиздак','Ебалротыч','Дерьмоедыч',
         'Мудозвоныч','Кто прочитал тот здохнет','Лохпидр','Даунич','Дрочевик','Говноедина','Хуй ебливый','Эщкере','ХУЙСОСИ',
         'Кто прочитал тот пидорас','СтоячийПенис','Пенисмон','Пенисдрочер','Гомоеблер','Гомик','Пикачу','Слоупок','Сукаблять']


@bot.message_handler(commands=['allpoke'])
def allpoke(m):
    i=0
    for ids in pokemons:
        i+=1
    bot.send_message(m.chat.id, 'Всего покемонов существует: '+str(i))

def unpoke(id):
    pokeban.remove(id)

@bot.message_handler(commands=['mypoke'])
def mypoke(m):
    x=pokemonss.find_one({'id':m.from_user.id})
    if x!=None:
        text=''
        for ids in x['pokemons']:
            text+='*'+ids+'*, '
        bot.send_message(m.chat.id, 'Ваши покемоны:\n\n'+text, parse_mode='markdown')
    else:
        bot.send_message(m.chat.id, 'Вы не открыли ни одного покеболла!')
           
           
           
           
@bot.message_handler(commands=['pokemon'])
def pokemon(m):
 x=banns(m.from_user.id, m.chat.id, m.from_user.first_name)
 if x==0:
  if m.from_user.id not in pokeban:
   x=pokemonss.find_one({'id':m.from_user.id})
   if x!=None:
    y=random.choice(pokemons)
    if y not in x['pokemons']:
        pokemonss.update_one({'id':m.from_user.id}, {'$push':{'pokemons':y}})
    bot.send_message(m.chat.id, 'Вам выпал покемон *'+y+'*!', parse_mode='markdown')
    pokeban.append(m.from_user.id)
    t=threading.Timer(60, unpoke, args=[m.from_user.id])
    t.start()
   else:
       pokemonss.insert_one({'id':m.from_user.id,
                            'pokemons':[]
                           })
       bot.send_message(m.chat.id, 'Вы создали дом для покемонов! Теперь настало время собрать их всех!')
  else:
      bot.send_message(m.chat.id, 'Покемона можно выбивать раз в минуту!')

def deletemin(id):
    try:
        del games[id]
        bot.send_message(id, 'Игра была отменена!')
    except:
        pass

@bot.message_handler(commands=['minimum'])
def unique(m):
    i=0
    for ids in games:
        if games[ids]['id']==m.chat.id:
            i=1
    if i==0:
        t=threading.Timer(300, deletemin, args=[m.chat.id])
        t.start()
        games.update(createminimum(m.chat.id, t))
        bot.send_message(m.chat.id, 'Присоединиться к игре можно командой /joinmin.')
        
@bot.message_handler(commands=['joinmin'])
def joinmin(m):
    i=0
    for ids in games:
        if games[ids]['id']==m.chat.id:
            game=games[ids]
            i=1
    if i==1:
        if m.from_user.id not in game['ids']:
          try:
            bot.send_message(m.from_user.id, 'Вы присоединились к игре "Минимум"!')
          except:
            bot.send_message(m.chat.id, m.from_user.first_name+', сначала напишите боту в личку!')
            return 0
          game['ids'].append(m.from_user.id)
          game['players'].update(createminplayer(m.from_user.id, m.from_user.first_name))
          bot.send_message(m.chat.id, m.from_user.first_name+' присоединился!')
            
            
@bot.message_handler(commands=['startmin'])
def startmin(m):
    i=0
    for ids in games:
        if games[ids]['id']==m.chat.id:
            game=games[ids]
            i=1
    if i==1:
        if len(game['players'])>2:
         if game['started']==0:
            game['started']=1
            game['timer'].cancel()
            t=threading.Timer(45, endxod, args=[game['id']])
            t.start()
            startminimum(m.chat.id)
            bot.send_message(m.chat.id, 'Игра началась! Перемещайтесь в личку к боту для выбора.')
        else:
            bot.send_message(m.chat.id, 'Недостаточно игроков!')
            
def endxod(id):
    for ids in games[id]['players']:
        x=games[id]['players'][ids]['number']
        idd=games[id]['players'][ids]['id']
        if x!=None:
            i=0
            for idss in games[id]['players']:
                if games[id]['players'][idss]['id']!=idd:
                    if games[id]['players'][idss]['number']==x:
                        i=1
            if i==1:
                games[id]['players'][ids]['win']=0
            else:
                games[id]['players'][ids]['win']=1
        else:
            games[id]['players'][ids]['win']=0
    winners={}       
    for ids in games[id]['players']:
            if games[id]['players'][ids]['win']==1:
                winners.update({games[id]['players'][ids]['id']:{'id':games[id]['players'][ids]['id'],
                                'number':games[id]['players'][ids]['number']
                               }})
    x=101
    for ids in winners:
        if winners[ids]['number']<x:
            x=winners[ids]['number']
    for ids in winners:
        if winners[ids]['number']==x:
            games[id]['players'][winners[ids]['id']]['finalwin']=1
    text1=''
    for ids in games[id]['players']:
        zz=games[id]['players'][ids]['name']+': Ничего\n'
        if games[id]['players'][ids]['number']!=None:
            zz=games[id]['players'][ids]['name']+': '+str(games[id]['players'][ids]['number'])+'\n'
        text1+=zz
    winner=None
    for ids in games[id]['players']:  
        if games[id]['players'][ids]['finalwin']==1:
            winner=games[id]['players'][ids]['name']
    if winner==None:
        winner='Победителя нет!'
    bot.send_message(id, 'Итоги игры:\nПоставленные числа:\n'+text1+'\nПобедитель: '+winner)
    del games[id]
            
def startminimum(id):
    for ids in games[id]['players']:
        try:
            bot.send_message(games[id]['players'][ids]['id'], 'Отправьте сюда натуральное число (от 1 и выше) и ожидайте результатов в беседе.')
        except:
            pass
        games[id]['players'][ids]['xod']=1
        
            
            

def createminplayer(id, name):
    return{id:{'id':id,
               'name':name,
               'number':None,
               'xod':0,
               'win':0,
               'finalwin':0
              }
          }
        
def createminimum(id, timerr):
    return{id:{'id':id,
               'players':{},
               'ids':[],
               'started':0,
               'timer':timerr
              }
          }
        
        
        
@bot.message_handler(commands=['gn'])
def guessnumber(m):
  q=guessrecs.find_one({'id':m.chat.id})
  if q==None:
        guessrecs.insert_one(createrec(m.chat.id))
  z=m.text.split(' ')
  if len(z)==2:
    try:
        y=int(z[1])
    except:
        bot.send_message(m.chat.id, 'Для игры нужно использовать формат:\n/gn *x*;\n1<=*x*<=100', parse_mode='markdown') 
        return 0
    if y>100 or y<1:
            bot.send_message(m.chat.id, 'x должен быть в пределах:\n1<=*x*<=100', parse_mode='markdown')
    else:
            x=guess.find({})
            i=0
            for ids in x:
                if ids['id']==m.chat.id:
                    i=1
                    chat=ids
            if i==1:
                guess.update_one({'id':m.chat.id},{'$inc':{'attemps':1}})
            else:
                guess.insert_one(createguess(m.chat.id))
            x=guess.find({})
            for ids in x:
                    if ids['id']==m.chat.id:
                        chat=ids
            if y==chat['number']:
                bot.send_message(m.chat.id, 'Попал! Верное число: *'+str(chat['number'])+'*.\nКоличество попыток: *'+str(chat['attemps'])+'*.', parse_mode='markdown')
                rec=guessrecs.find_one({'id':m.chat.id})
                if rec['record']!=None:
                  if chat['attemps']+1<rec['record']:
                    guessrecs.update_one({'id':m.chat.id}, {'$set':{'record':chat['attemps']}})
                else:
                    guessrecs.update_one({'id':m.chat.id}, {'$set':{'record':chat['attemps']}})
                guess.remove({'id':m.chat.id})
            elif y<chat['number']:
                bot.send_message(m.chat.id, 'Число '+str(y)+' меньше загаданного! Количество попыток: '+str(chat['attemps']))
            elif y>chat['number']:
                bot.send_message(m.chat.id, 'Число '+str(y)+' больше загаданного! Количество попыток: '+str(chat['attemps']))
                
        
@bot.message_handler(commands=['top'])
def top(m):
    try:
           x=guessrecs.find_one({'id':m.chat.id})
           bot.send_message(m.chat.id, 'Рекорд этого чата: '+str(x['record']))
    except:
        bot.send_message(m.chat.id, 'В этом чате не было сыграно ни одной игры!')


def createrec(id):
    return{'id':id,
           'record':None
          }
        

def createguess(id):
    return{'id':id,
           'attemps':1,
           'number':random.randint(1,100)
          }
        
        

def unwarn(id):
    try:
        del timers[id]
    except:
        pass


def unban(id):
    try:
        ban.remove(id)
    except:
        pass

    
def banns(id, chatid, name):
    i=0
    for ids in timers:
        if timers[ids]['id']==id:
            i=1
    if i==0:
        print('1')
        timers.update({id:{'id':id,
                          'messages':0}})
        t=threading.Timer(15, unwarn, args=[id])
        t.start()
    else:
        print('2')
        timers[id]['messages']+=1
        if timers[id]['messages']>=4:
            bot.send_message(chatid, 'Пользователь '+name+' много спамил и был заблокирован на 20 секунд.')
            ban.append(id)
            t=threading.Timer(20, unban, args=[id])
            t.start()
            return 1
    return 0
    
    
@bot.message_handler(commands=['stats'])
def statss(m):
 if m.from_user.id not in ban:
   x=banns(m.from_user.id, m.chat.id, m.from_user.first_name)
   if x==0:
    x=users.find_one({'id':m.from_user.id})
    if x!=None:
      try:
        bot.send_message(m.chat.id, 'Статистика пользователя (по всем чатам):\n'+
                         'Боёв проведено: '+str(x['games'])+'\n'+
                         'Побед: '+str(x['wins'])+'\n'+
                         'Поражений (смертей): '+str(x['looses'])+'\n'+
                         'Процент побед: '+str(int((round(x['wins']/x['games'], 2))*100))+'%')
      except:
            bot.send_message(m.chat.id, 'Вы еще не провели ни одного боя!')

@bot.message_handler(commands=['flee'])
def flee(m):
           pass

   
@bot.message_handler(commands=['help'])
def help(m):
    bot.send_message(m.chat.id, 'Цель этой игры очень проста - побеждать в боях. Чтобы победить, нужно выбрать правильного соперника. '+
                     'Как же это сделать? Очень просто. По команде /roles вам будет выведен список того, кто кого 100% побеждает в бою '+
                     '(Одинаковые роли имеют 50% шанс друг против друга). После вашей смерти вам выдается случайная роль, которую никто не знает, пока '+
                     'вы не вступите в следующий бой. Сражаться можно раз в минуту.')
    
    
@bot.message_handler(commands=['roles'])
def roles(m):
    bot.send_message(m.chat.id, 'Кто кого выигрывает в бою:\n\n'+
'''*Волк*: ниндзя, кот, медведь

*Стрелок*: волк, ниндзя, кот

*Колдун*: волк, стрелок, убийца

*Ниндзя*: колдун, убийца, медведь

*Кот*: колдун, ниндзя, медведь

*Убийца*: волк, кот, стрелок

*Медведь*: стрелок, колдун, убийца''', parse_mode='markdown')


           
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
 if m.from_user.id not in ban:
   x=banns(m.from_user.id, m.chat.id, m.from_user.first_name)
   if x==0:
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
 if m.from_user.id not in ban:
  x=banns(m.from_user.id, m.chat.id, m.from_user.first_name)
  if x==0:
   name=users.find_one({'id':m.from_user.id})
   if name!=None:
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
           bot.send_message(m.chat.id, 'Используйте формат:\n/fight *имя_бойца*', parse_mode='markdown')
    else:
           bot.send_message(m.chat.id, 'Сначала дайте персонажу имя! (/name)')
            
            
@bot.message_handler(commands=['users'])
def userssss(m):
  if m.from_user.id not in ban:
    x=banns(m.from_user.id, m.chat.id, m.from_user.first_name)
    if x==0:
      x=chats.find_one({'id':m.chat.id})
      if x!=None:
           text=''
           y=users.find({})
           for ids in y:
                if ids['id'] in x['users']:
                     text+=ids['nameofuser']+' (`'+ids['name']+'`)'+'\n'
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
    if x=='mage':
        role='Колдун'
    if x=='nindza':
        role='Ниндзя'
    if x=='cat':
        role='Кот'
    if x=='killer':
        role='Убийца'
    if x=='bear':
        role='Медведь'
    return role

def unbattle(id1, id2):
    users.update_one({'id':id1}, {'$set':{'fighting':0}})
    users.update_one({'id':id2}, {'$set':{'fighting':0}})

def fight(x,y, id):
    if x['id']!=y['id']:
     if x['fighting']==0:
      if y['fighting']==0:
        users.update_one({'id':x['id']}, {'$set':{'fighting':1}})
        users.update_one({'id':y['id']}, {'$set':{'fighting':1}})
        t=threading.Timer(60, unbattle, args=[x['id'], y['id']])
        t.start()
        result=fight2(x['role'], y['role'], id)
        if result[1]=='x':
            winner=x
            looser=y
        else:
            winner=y
            looser=x
        zzz=random.choice(rolelist)
        users.update_one({'id':looser['id']}, {'$set':{'role':zzz}})
        try:
           bot.send_message(looser['id'], 'Вы погибли! Ваша новая роль: '+roletoname(zzz)+'.')
        except:
           pass
        bot.send_message(id, result[0]+'Победа `'+winner['name']+'` ('+roletoname(winner['role'])+')!', parse_mode='markdown')
        users.update_one({'id':winner['id']}, {'$inc':{'games':1}})
        users.update_one({'id':winner['id']}, {'$inc':{'wins':1}})
        
        users.update_one({'id':looser['id']}, {'$inc':{'games':1}})
        users.update_one({'id':looser['id']}, {'$inc':{'looses':1}})
        users.update_one({'id':looser['id']}, {'$inc':{'dies':1}})
      else:
        bot.send_message(id, 'Выбранный соперник отдыхает после предыдущего сражения.')
     else:
        bot.send_message(id, 'Вы отдыхаете после предыдущего сражения. Сражаться можно раз в минуту.')
    else:
        bot.send_message(id, 'Нельзя сражаться с самим собой!')





def fight2(x, y, id):
    returned=[]             
    if x=='wolf':
        if y=='wolf':
            text='*Волк* _vs_ *Волк*\n'
            returned.append(text)
            a=random.randint(1,100)
            if a<=50:
                winner='x'
            else:
                winner='y'
            returned.append(winner)
        elif y=='gunner':
            a=random.randint(1,100)
            text='*Волк* _vs_ *Стрелок*\n'
            if a<=0:
                winner='x'
            else:
                winner='y'
            returned.append(text)
            returned.append(winner)
        elif y=='mage':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Волк* _vs_ *Колдун*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='nindza':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Волк* _vs_ *Ниндзя*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='cat':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Волк* _vs_ *Кот*\n'
            returned.append(text)
            returned.append(winner) 
        elif y=='killer':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Волк* _vs_ *Убийца*\n'          
            returned.append(text)
            returned.append(winner)
        elif y=='bear':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Волк* _vs_ *Медведь*\n'
            returned.append(text)
            returned.append(winner)
           
           
    elif x=='gunner':
        if y=='wolf':
            text='*Стрелок* _vs_ *Волк*\n'
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            returned.append(text)
            returned.append(winner)
        elif y=='gunner':
            a=random.randint(1,100)
            if a<=50:
                winner='x'
            else:
                winner='y'
            text='*Стрелок* _vs_ *Стрелок*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='mage':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
                text='\n'
            else:
                winner='y'
                text='\n'
            text='*Стрелок* _vs_ *Колдун*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='nindza':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
                text='\n'
            else:
                winner='y'
                text='\n'
            text='*Стрелок* _vs_ *Ниндзя*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='cat':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
                text='\n'
            else:
                winner='y'
                text='\n'
            text='*Стрелок* _vs_ *Кот*\n'
            returned.append(text)
            returned.append(winner) 
        elif y=='killer':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
                text='\n'
            else:
                winner='y'
                text='\n'
            text='*Стрелок* _vs_ *Убийца*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='bear':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Стрелок* _vs_ *Медведь*\n'
            returned.append(text)
            returned.append(winner)
        
        
    elif x=='mage':
        if y=='wolf':
            text='*Колдун* _vs_ *Волк*\n'
            returned.append(text)
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            returned.append(winner)
        elif y=='gunner':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Колдун* _vs_ *Стрелок*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='mage':
            a=random.randint(1,100)
            if a<=50:
                winner='x'
            else:
                winner='y'
            text='*Колдун* _vs_ *Колдун*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='nindza':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Колдун* _vs_ *Ниндзя*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='cat':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Колдун* _vs_ *Кот*\n'
            returned.append(text)
            returned.append(winner) 
        elif y=='killer':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
                text='\n'
            else:
                winner='y'
            text='*Колдун* _vs_ *Убийца*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='bear':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Колдун* _vs_ *Медведь*\n'
            returned.append(text)
            returned.append(winner)
           
           
    elif x=='nindza':
        if y=='wolf':
            text='*Ниндзя* _vs_ *Волк*\n'
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            returned.append(text)
            returned.append(winner)
        elif y=='gunner':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Ниндзя* _vs_ *Стрелок*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='mage':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Ниндзя* _vs_ *Колдун*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='nindza':
            a=random.randint(1,100)
            if a<=50:
                winner='x'
            else:
                winner='y'
            text='*Ниндзя* _vs_ *Ниндзя*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='cat':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Ниндзя* _vs_ *Кот*\n'
            returned.append(text)
            returned.append(winner) 
        elif y=='killer':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Ниндзя* _vs_ *Убийца*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='bear':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Ниндзя* _vs_ *Медведь*\n'
            returned.append(text)
            returned.append(winner)
           
           
    elif x=='cat':
        if y=='wolf':
            text='*Кот* _vs_ *Волк*\n'
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            returned.append(text)
            returned.append(winner)
        elif y=='gunner':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Кот* _vs_ *Стрелок*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='mage':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Кот* _vs_ *Колдун*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='nindza':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Кот* _vs_ *Ниндзя*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='cat':
            a=random.randint(1,100)
            if a<=50:
                winner='x'
            else:
                winner='y'
            text='*Кот* _vs_ *Кот*\n'
            returned.append(text)
            returned.append(winner) 
        elif y=='killer':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Кот* _vs_ *Убийца*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='bear':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Кот* _vs_ *Медведь*\n'
            returned.append(text)
            returned.append(winner)
           
           
    elif x=='killer':
        if y=='wolf':
            text='*Убийца* _vs_ *Волк*\n'
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            returned.append(text)
            returned.append(winner)
        elif y=='gunner':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Убийца* _vs_ *Стрелок*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='mage':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Убийца* _vs_ *Колдун*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='nindza':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Убийца* _vs_ *Ниндзя*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='cat':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Убийца* _vs_ *Кот*\n'
            returned.append(text)
            returned.append(winner) 
        elif y=='killer':
            a=random.randint(1,100)
            if a<=50:
                winner='x'
            else:
                winner='y'
            text='*Убийца* _vs_ *Убийца*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='bear':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Убийца* _vs_ *Медведь*\n'
            returned.append(text)
            returned.append(winner)
                      
                      
    elif x=='bear':
        if y=='wolf':
            text='*Медведь* _vs_ *Волк*\n'
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            returned.append(text)
            returned.append(winner)
        elif y=='gunner':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Медведь* _vs_ *Стрелок*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='mage':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Медведь* _vs_ *Колдун*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='nindza':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Медведь* _vs_ *Ниндзя*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='cat':
            a=random.randint(1,100)
            if a<=0:
                winner='x'
            else:
                winner='y'
            text='*Медведь* _vs_ *Кот*\n'
            returned.append(text)
            returned.append(winner) 
        elif y=='killer':
            a=random.randint(1,100)
            if a<=100:
                winner='x'
            else:
                winner='y'
            text='*Медведь* _vs_ *Убийца*\n'
            returned.append(text)
            returned.append(winner)
        elif y=='bear':
            a=random.randint(1,100)
            if a<=50:
                winner='x'
            else:
                winner='y'
            text='*Медведь* _vs_ *Медведь*\n'
            returned.append(text)
            returned.append(winner)

    return returned


@bot.message_handler(commands=['name'])
def name(m):
  if m.from_user.id not in ban:
   x=banns(m.from_user.id, m.chat.id, m.from_user.first_name)
   if x==0:
    text=m.text.split(' ')
    if len(text)==2:
        if len(text[1])<=25:
          i=0
          for symbol in text[1]:
            if symbol.lower() not in symbollist:
                i=1
          if i==0:
            zz=users.find({})
            spisok=[]
            for ids in zz:
                try:
                      spisok.append(ids['name'].lower())
                except:
                      pass
            if text[1].lower() not in spisok:
                x=users.find_one({'id':m.from_user.id})
                users.update_one({'id':m.from_user.id}, {'$set':{'name':text[1]}})
                bot.send_message(m.chat.id, 'Вы успешно изменили имя на '+text[1]+'!')
            else:
                bot.send_message(m.chat.id, 'Такое имя уже занято!')
          else:
            bot.send_message(m.chat.id, 'В нике можно использовать только:\nРусский алфавит;\nАнглийский алфавит;\nЦифры.')
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
           'games':0,
           'fighting':0
          }

@bot.message_handler(content_types=['text'])
def textt(m):
    x=chats.find_one({'id':m.chat.id})
    if x==None:
        chats.insert_one(createchat(m.chat.id))
    if users.find_one({'id':m.from_user.id})!=None:
           users.update_one({'id':m.from_user.id}, {'$set':{'nameofuser':m.from_user.first_name}})
    i=0
    for ids in games:
        if m.from_user.id in games[ids]['ids']:
            game=games[ids]
            i=1
    if i==1:
      if m.from_user.id==m.chat.id:
        if game['players'][m.from_user.id]['xod']==1:
            try:
                x=int(m.text)
            except:
                bot.send_message(m.chat.id, 'Введите натуральное число (1 или больше)!')
                return 0
            if x>=1 and x<=1000:
                game['players'][m.from_user.id]['xod']=0
                game['players'][m.from_user.id]['number']=x
                bot.send_message(m.chat.id, 'Вы сделали выбор: '+str(x)+'. Ожидайте результатов...')
            else:
                      bot.send_message(m.chat.id, 'Слишком большое число, не страдай хуйнёй')
            
      
  
  
if True:
 try:
   print('7777')

   users.update_many({}, {'$set':{'fighting':0}})
    
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
       
