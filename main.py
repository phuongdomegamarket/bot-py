import asyncio
import os
import re,json
import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.utils import get
import random
import datetime
import server
from guild import *
from acb import *
import aiohttp
server.b()
USERNAME=os.environ.get('username')
PASSWORD=os.environ.get('password')

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
VIETTELS='032, 033, 034, 035, 036, 037, 038, 039, 096, 097, 098, 086'
VIETTELS=VIETTELS.split(',')
VINAPHONES=' 091, 094, 088, 081, 082, 083, 084, 085'
VINAPHONES=VINAPHONES.split(',')
VIETNAMOBILE='052, 056, 058, 092'
VIETNAMOBILE=VIETNAMOBILE.split(',')
HEADERS = []
THREADS = []
USERNAMES = [] 
GUILDID = 1236962671824211998 
RESULT=None

def correctSingleQuoteJSON(s):
    rstr = ""
    escaped = False

    for c in s:
    
        if c == "'" and not escaped:
            c = '"' # replace single with double quote
        
        elif c == "'" and escaped:
            rstr = rstr[:-1] # remove escape character before single quotes
        
        elif c == '"':
            c = '\\' + c # escape existing double quotes
   
        escaped = (c == "\\") # check for an escape character
        rstr += c # append the correct json
    
    return rstr
INFO=False
@client.event
async def on_ready():
    global INFO,RESULT
    try:
      req=requests.get('http://localhost:8888')
      print(req.status_code)
    except:
      server.b()
      guild = client.get_guild(GUILDID)
      rs=await login(USERNAME,PASSWORD)
      RESULT=await getBasic(guild)
      if rs:
        INFO=rs
      if not getTransAcb.is_running():
        getTransAcb.start(guild)

    
    
@client.event
async def  on_disconnect():
  global RESULT
  if RESULT:
    acbThread=None
    for thread in RESULT['banksCh'].threads:
      if 'acb' in thread.name:
        acbThread=thread
    if acbThread:
      msgs=[msg async for msg in acbThread.history()]
      if len(msgs)>0:
        old=re.search('.*Sessions are `(.*?)`.*',msgs[0].content).group(1)
        i=int(old)-1 if int(old)>0 else 0
        await msgs[0].edit(content='Sessions are `'+str(i)+'` actived')

@tasks.loop(seconds=1)
async def getTransAcb(guild): 
  global INFO
  print('getTransAcb is running')
  if INFO:
    try:
      rs1=await getListAccount(INFO)
      for item in rs1['list']:
        list=await getBalance(INFO,item['accountNumber'])
        basic=await getBasic(guild)
        threads=basic['acbCh'].threads+[thread async for thread in basic['acbCh'].archived_threads()]
        if list:
          data=list['data'][::-1]
          for item in data:
            applied_tags=[]
            if str(item['activeDatetime']) not in str(threads):
              tags=basic['acbCh'].available_tags
              st=''
              if item['type'].lower()=='in':
                for tag in tags:
                  if 'in' in tag.name.lower() or 'chuyển đến' in tag.name.lower():
                    applied_tags.append(tag)
              else:
                for tag in tags:
                  if 'out' in tag.name.lower() or 'chuyển đi' in tag.name.lower():
                    applied_tags.append(tag)
                if 'bankName' in item and item['bankName']!='':
                  st+='\nĐến ngân hàng: **'+item['bankName']+'**\n'
                if 'receiverAccountNumber' in item and item['receiverAccountNumber']!='':
                  st+='\nĐến số tài khoản: **'+item['receiverAccountNumber']+'**'
                if 'receiverName' in item and item['receiverName']!='':
                  st+='\nĐến chủ tài khoản: **'+item['receiverName']+'**'
              allowed_mentions = discord.AllowedMentions(everyone = True)
              amount=str(item['amount']).split('.')[0]
              amount=[f'{cur:,}' for cur in [int(amount)]][0]
              time=datetime.datetime.fromtimestamp(item['activeDatetime']/1000)
              day=time.day if time.day>9 else '0'+str(time.day)
              month=time.month if time.month>9 else '0'+str(time.month)
              hour=time.hour if time.hour>9 else '0'+str(time.hour)
              minute=time.minute if time.minute>9 else '0'+str(time.minute)
              second=time.second if time.second>9 else '0'+str(time.second)
              timestr=f'{day}/{month}/{time.year} {hour}:{minute}:{second}'
              thread=await basic['acbCh'].create_thread(name=('+ ' if item['type'].lower()=='in' else '- ')+amount+' '+item['currency']+'/ '+str(item['activeDatetime']),content='\nSố tiền: **'+amount+' '+item['currency']+'**\nNội dung: **'+item['description']+'**\nBiến động trên STK: **'+str(item['account'])+'**\nThời điểm: **'+timestr.split(' ')[1]+'** ngày **'+timestr.split(' ')[0]+'**'+st+'\n@everyone',applied_tags =applied_tags )
        else:
          rs=await login(USERNAME,PASSWORD)
          if rs:
            INFO=rs
    except Exception as error:
      print(error)
      rs=await login(USERNAME,PASSWORD)
      if rs:
        INFO=rs
              
client.run(os.environ.get('botToken'))
