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
from twitter_bot import set_up_twitter_api
from discord.ext.commands import Bot
from discord.ext import commands
from fake_useragent import UserAgent
from dotenv import dotenv_values

dateFormat = '%b %d %Y %I:%M%p'

itemsProcessed = 0

threadBlocked = False

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
twitter_api = set_up_twitter_api()

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

PublisherNameToDiscordChannelNameMap = { 
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
    TEST_CHANNEL : {},
    KODANSHA_CHANNEL : {},
    VIZ_CHANNEL : {},
    VERTICAL_CHANNEL : {},
    DARK_HORSE_CHANNEL : {},
    SEVENS_SEAS_CHANNEL : {},
    SQUARE_ENIX_CHANNEL : {},
    UDON_CHANNEL : {},
    YEN_PRESS_CHANNEL: {},
    ANIME_CHANNEL : {},
  }   
}

async def triplePrint(discordChannel, message, discordMessageParts=""):
  try:
    await doublePrint(discordChannel, message, discordMessageParts)
    twitter_api.PostUpdate(message)
  except: 
    print('Maybe error posting to twitter')

async def doublePrint(discordChannel, message, discordMessageParts=""):
  try:
    await guildChannelList[MY_GUILD_NAME][discordChannel].send(discordMessageParts + message)
  except: 
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print('error posting to discord: [' + message + ']')
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    traceback.print_exc()
  print()
  print(message)

def makeRSURL(page = 0, publisher = 'VIZ-BOOKS'):
  increments = 96
  rsLinkParts = [
    'https://www.rightstufanime.com/api/items?c=546372&country=US&currency=USD',
    '&custitem_rs_publisher=',
    publisher,
    '&custitem_rs_web_class=Manga&fieldset=search&language=en&limit=',
    str(increments),
    '&n=2&offset=',
    str(increments*page),
    '&pricelevel=5&sort=relevance%3Aasc&use_pcv=F'
  ]

  return ''.join(rsLinkParts)

def makeRSAnimeURL(page = 0): 
  increments = 96
  rsLinkParts = [
    'https://www.rightstufanime.com/api/items?c=546372&country=US&currency=USD',
    '&custitem_rs_adult=false&custitem_rs_web_class=Blu~ray,DVD&fieldset=search&include=facets&language=en&',
    'limit=',
    str(increments),
    '&n=2&offset=',
    str(increments*page),
    '&pricelevel=5&sort=relevance:asc&use_pcv=F'
  ]

  return ''.join(rsLinkParts)


def printProgressBar (iteration, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
  """
  Call in a loop to create terminal progress bar
  @params:
      iteration   - Required  : current iteration (Int)
      total       - Required  : total iterations (Int)
      prefix      - Optional  : prefix string (Str)
      suffix      - Optional  : suffix string (Str)
      decimals    - Optional  : positive number of decimals in percent complete (Int)
      length      - Optional  : character length of bar (Int)
      fill        - Optional  : bar fill character (Str)
      printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
  """
  if iteration%1000 == 0: 
    print()
  
  filledLength = int(length * (iteration%1000+1) // 1000)
  bar = fill * filledLength + '-' * (length - filledLength)
  print(f'\r{prefix} |{bar}| {suffix}', end = printEnd)
  # Print New Line on Complete

###################################
def processItem(item, foundURL, now):
  i = {}
  i['name'] = item['storedisplayname']
  i['price'] = item['onlinecustomerprice_formatted']
  i['purchasable'] = item['isinstock']
  i['url'] = 'https://www.rightstufanime.com/' + item['urlcomponent']
  i['found_on_url'] = foundURL
  if 'custitem_rs_new_releases_preorders' in item:
    if item['custitem_rs_new_releases_preorders'] == None or 'None' in item['custitem_rs_new_releases_preorders'] or 'New Release' in item['custitem_rs_new_releases_preorders']:
      i['preorder'] = False
    elif 'Pre-order' in item['custitem_rs_new_releases_preorders']:
      i['preorder'] = True  
    else: 
      print(item['custitem_rs_new_releases_preorders'])
      print('**********FUCKKKKK**************')
  else: 
    i['preorder'] = False
  if 'custitem_damaged_type' in item:
    if item['custitem_damaged_type'] == 'Imperfect':
      i['imperfect'] = True
    else:
      i['imperfect'] = False
    if item['custitem_damaged_type'] == 'Damaged':
      i['damaged'] = True
    else:
      i['damaged'] = False
  if 'upccode' in item:
    i['upccode'] = item['upccode'] 
  i['last_checked'] = now.strftime(dateFormat)
  return i
###################################

async def compareItemAndPublishMessage(i, productCatalog, now, mDict, publisher):
  changes = False
  url = i['url']
  nameAndURL = + i['name'] + '\n' + url
  if url in productCatalog:
    if 'damaged' in i and i['damaged'] and i['purchasable'] and not productCatalog[url]['purchasable']:
      mDict['damagedMismatch'] +=1 
      changes = True
      i['in-stock-time'] = now.strftime(dateFormat)
      await doublePrint(PublisherNameToDiscordChannelNameMap[publisher], '**[Damaged]**\n' + nameAndURL, "")
    elif 'imperfect' in i and i['imperfect'] and i['purchasable'] and not productCatalog[url]['purchasable']:
      mDict['imperfectMismatch'] +=1
      changes = True
      i['in-stock-time'] = now.strftime(dateFormat)
      await doublePrint(PublisherNameToDiscordChannelNameMap[publisher], '**[Imperfect]**\n' + nameAndURL, "")
    elif i['purchasable'] and productCatalog[url]['preorder'] and not i['preorder']:
      mDict['mismatches'] += 1
      mDict['preorderMismatch'] += 1
      changes = True
      i['in-stock-time'] = now.strftime(dateFormat)
      await triplePrint(PublisherNameToDiscordChannelNameMap[publisher], '**[Preorder Now In Stock]**\n' + nameAndURL, "")
    elif productCatalog[url]['purchasable'] and not i['purchasable'] and not productCatalog[url]['preorder']:
      mDict['mismatches'] += 1
      mDict['outOfStockMismatch'] += 1
      changes = True
      i['out-of-stock-time'] = now.strftime(dateFormat)
      await doublePrint(PublisherNameToDiscordChannelNameMap[publisher], '**[OUT OF STOCK]**\n' + nameAndURL, "")
    elif not productCatalog[url]['purchasable'] and i['purchasable']:
      mDict['mismatches'] += 1
      mDict['inStockMismatch'] += 1
      changes = True
      i['in-stock-time'] = now.strftime(dateFormat)
      await triplePrint(PublisherNameToDiscordChannelNameMap[publisher], '**[RESTOCK]**\n' + nameAndURL, "")    
  else:
    if i['preorder']:
      changes = True
      i['pre-order-time'] = now.strftime(dateFormat)
      await triplePrint(PublisherNameToDiscordChannelNameMap[publisher], '**[NEW]**\n' + nameAndURL, "")
    elif 'damaged' in i and i['damaged']:
      changes = True
      i['in-stock-time'] = now.strftime(dateFormat)
      await doublePrint(PublisherNameToDiscordChannelNameMap[publisher], '**[Damaged]**\n' + nameAndURL, "")
    elif 'imperfect' in i and i['imperfect']:
      changes = True
      i['in-stock-time'] = now.strftime(dateFormat)
      await doublePrint(PublisherNameToDiscordChannelNameMap[publisher], '**[Imperfect]**\n' + nameAndURL, "")
    elif i['purchasable']:
      changes = True
      i['in-stock-time'] = now.strftime(dateFormat)
      await triplePrint(PublisherNameToDiscordChannelNameMap[publisher], '**[NEW]**\n' + nameAndURL, "")
    else: 
      changes = True
      i['out-of-stock-time'] = now.strftime(dateFormat)
      await doublePrint(PublisherNameToDiscordChannelNameMap[publisher], 'New Item scanned in out of stock:\n' + nameAndURL, "")  
  return changes

###################################
async def runApp():
  global itemsProcessed

  mDict = {
    'mismatches': 0,
    'preorderMismatch': 0,
    'inStockMismatch': 0,
    'outOfStockMismatch': 0,
    'damagedMismatch': 0,
    'imperfectMismatch': 0
  }

  productCatalog = json.load( open( "right_stuf_anime.json" ) )

  with open("right_stuf_anime.on_start_backup.json", "w") as outfile:
    json.dump( productCatalog, outfile)

  for publisher in PUBLISHERS:
    publisherStartTime = datetime.datetime.now()
    page = 0
    itemsProcessedForPublisher = 0
    print(publisher)
    
    while True:
      url = ""
      if publisher == ANIME:
        url = makeRSAnimeURL(page)
      else:
        url = makeRSURL(page, publisher)
      #print(url)
      ua = UserAgent()
      headers = {'User-Agent': ua.random}

      await asyncio.sleep(0.15)
      request = requests.get(url, headers=headers)

      if request.status_code == 400:
        print("$$$$$$$$$$ Bad page load detected at page: " + str(page))
        break
      if request.status_code != 200:
        print('$$$$$$$$$$ Weird status code: ' + str(request.status_code))
        continue  
 
      if 'items' not in request.json():
        print('uh oh shit************')

      items = request.json()['items']

      now = datetime.datetime.now()
      changes = False
      # Scan page of items loop
      for item in items:
        await asyncio.sleep(0.13)
        i = processItem(item, url, now)
        itemsProcessed += 1
        itemsProcessedForPublisher += 1
        printProgressBar(itemsProcessedForPublisher, prefix = 'Progress:', suffix = str(itemsProcessedForPublisher), length = 50)
        changes = await compareItemAndPublishMessage(i, productCatalog, now=now, mDict=mDict, publisher=publisher)
        
        productCatalog[i['url']] = i

      # Dump changes to disk
      if changes:
        print('Dumping changes to disk...')
        with open("right_stuf_anime._change_dump_backup.json", 'w') as outfile:
          json.dump(productCatalog,  outfile)
        with open("right_stuf_anime.json", 'w') as outfile:
          json.dump(productCatalog,  outfile)

      # Check for next query page
      nextPageFound = False
      if 'links' in request.json():
        for item in request.json()['links']:
          if 'rel' in item:
            if item['rel'] == 'next':
                nextPageFound = True
                page += 1

      if not nextPageFound: 
        print() 
        print('Last page: ' + str(page))
        break

    publisherEndTime = datetime.datetime.now()
    print('------------------------------------------------')
    print('Publisher: ' + publisher)
    print('Mismatches This Session: ' + str(mDict['mismatches']))
    print('In Stock mismatches: ' + str(mDict['inStockMismatch']))
    print('Out Of Stock mismatches: ' + str(mDict['outOfStockMismatch']))
    print('Preorder Mismatches: ' + str(mDict['preorderMismatch']))
    print('Damaged Mismatches: ' + str(mDict['damagedMismatch']))
    print('Imperfect Mismatches: ' + str(mDict['imperfectMismatch']))
    print('End time: ' + publisherEndTime.strftime(dateFormat))
    print('Total time: ' + str(publisherEndTime-publisherStartTime))
    print('Total time per page: ' + str((publisherEndTime-publisherStartTime)/(page+1)))
    print('Items processed this publisher: ' + str(itemsProcessedForPublisher)) 
    print('Items processed this session: ' + str(itemsProcessed))  
    print('------------------------------------------------')
    with open("right_stuf_anime._publisher_done_dump_backup.json", 'w') as outfile:
      json.dump(productCatalog,  outfile)
    with open("right_stuf_anime.json", 'w') as outfile:
      json.dump(productCatalog,  outfile)
  await doublePrint(TEST_CHANNEL, "Loop complete.")
###################################


client = discord.Client()

discordSecret = config['TOKEN']

@client.event
async def on_ready():
  global threadBlocked
  random.shuffle(PUBLISHERS)
  print(f'{client.user.name} has connected to Discord!')
  for guild in client.guilds:
    if guild.name in guildChannelList:
      print('[Guild]: ' + guild.name)
      for channel in guild.channels:
        if channel.name in guildChannelList[guild.name]:
          print('[Channel]: ' + channel.name)
          guildChannelList[guild.name][channel.name] = client.get_channel(channel.id)
        else: print('fix: [' + channel.name + ']')
  print('Publishers loaded:')
  for publisher in PUBLISHERS: 
    print(publisher)
  if not threadBlocked:
    threadBlocked = True
    try:
      await doublePrint(TEST_CHANNEL, 'App booting up...')
      while True: 
        await runApp()
    finally: 
      threadBlocked = False
  else: 
    doublePrint(TEST_CHANNEL, "Thread blocked!!!")

client.run(discordSecret)