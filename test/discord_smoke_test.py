import requests
import json
import datetime
import time
import os
import random
import discord
import asyncio
import traceback
import twitter

from discord.ext.commands import Bot
from discord.ext import commands
from fake_useragent import UserAgent
from dotenv import dotenv_values



PUBLISHERS = [
  'KODANSHA-COMICS',
  'YEN-PRESS',
  'VIZ-BOOKS',
  'UDON-ENTERTAINMENT',
  'VERTICAL',
  'DARK-HORSE',
  'DARK-HORSE-MANGA',
  'SEVEN-SEAS',
  'SQUARE-ENIX-MANGA',
  'ANIME'
]

config = dotenv_values(".env")

MY_GUILD_NAME = 'Jake\'s Manga In-Stock Tracker (RightStufAnime)'

IN_STOCK_CHANNEL = 'in_stock'
OUT_OF_STOCK_CHANNEL = 'out_of_stock'
DAMAGED_AND_IMPERFECT_CHANNEL = 'damaged_and_imperfect'
PREORDERS_CHANNEL = 'preorders'
TEST_CHANNEL = 'testing_please_ignore'
ANIME_CHANNEL = 'anime'
KODANSHA_CHANNEL = 'kodansha_comics'
YEN_PRESS_CHANNEL = 'yen_press'
VIZ_CHANNEL = 'viz_books'
UDON_CHANNEL = 'udon_entertainment'
VERTICAL_CHANNEL = 'vertical'
DARK_HORSE_CHANNEL = 'dark_horse'
SEVENS_SEAS_CHANNEL = 'seven_seas'
SQUARE_ENIX_CHANNEL = 'square_enix_manga'

##### RS Manga publishers
KODANSHA = 'KODANSHA-COMICS'
YEN_PRESS = 'YEN-PRESS'
VIZ = 'VIZ-BOOKS'
UDON = 'UDON-ENTERTAINMENT'
VERTICAL = 'VERTICAL'
DARK_HORSE = 'DARK-HORSE'
DARK_HORSE_MANGA = 'DARK-HORSE-MANGA'
SEVEN_SEAS = 'SEVEN-SEAS'
SQUARE_ENIX = 'SQUARE-ENIX-MANGA'
ANIME = 'ANIME'

DiscordChannelMap = { 
  ANIME: ANIME_CHANNEL,
  DARK_HORSE : DARK_HORSE_CHANNEL,
  DARK_HORSE_MANGA : DARK_HORSE_CHANNEL,
  KODANSHA : KODANSHA_CHANNEL,
  SEVEN_SEAS : SEVENS_SEAS_CHANNEL,
  SQUARE_ENIX : SQUARE_ENIX_CHANNEL,
  UDON : UDON_CHANNEL,
  VERTICAL : VERTICAL_CHANNEL,
  VIZ : VIZ_CHANNEL,
  YEN_PRESS : YEN_PRESS_CHANNEL,
}

publisherNameHumanReadable = {
  ANIME: 'Anime',
  DARK_HORSE : 'Dark Horse',
  DARK_HORSE_MANGA : 'Dark Horse',
  KODANSHA : 'Kodansha Comics',
  SEVEN_SEAS : 'Seven Seas',
  SQUARE_ENIX : 'Square Enix Manga',
  UDON : 'Udon Entertainment',
  VERTICAL : 'Vertical',
  VIZ : 'Viz Books',
  YEN_PRESS : 'Yen Press'
}

guildChannelList = { 
  MY_GUILD_NAME : { 
    IN_STOCK_CHANNEL : {}, 
    OUT_OF_STOCK_CHANNEL : {}, 
    DAMAGED_AND_IMPERFECT_CHANNEL : {}, 
    PREORDERS_CHANNEL : {},
    KODANSHA_CHANNEL : {},
    VIZ_CHANNEL : {},
    VERTICAL_CHANNEL : {},
    DARK_HORSE_CHANNEL : {},
    SEVENS_SEAS_CHANNEL : {},
    SQUARE_ENIX_CHANNEL : {},
    ANIME_CHANNEL : {},
  }   
}



client = discord.Client()

discordSecret = config['TOKEN']

print('testsetst')
@client.event
async def on_ready():
  global threadBlocked
  random.shuffle(PUBLISHERS)
  print('testsetstsad')
  print(f'{client.user.name} has connected to Discord!')
  for guild in client.guilds:
    print(guild.name)
    for channel in guild.channels:
        print(channel.name)
    if guild.name in guildChannelList:
      print('[Guild]: ' + guild.name)
      for channel in guild.channels:
        if channel.name in guildChannelList[guild.name]:
          print('[Channel]: ' + channel.name)
          guildChannelList[guild.name][channel.name] = client.get_channel(channel.id)
        else: print('fix:        ' + channel.name)
  print('Publishers loaded:')
  for publisher in PUBLISHERS: 
    print(publisher)
  
client.run(discordSecret)