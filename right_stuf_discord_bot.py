import requests
import json
import datetime
import time
import os
import random
import discord
from discord.ext.commands import Bot
from discord.ext import commands
from fake_useragent import UserAgent
from dotenv import dotenv_values

dateFormat = '%b %d %Y %I:%M%p'

totalMismatches = 0
damaged = 0
imperfect = 0
preorders = 0
purchasable = 0
itemsProcessed = 0

PUBLISHERS = [
  'KODANSHA-COMICS',
  'YEN-PRESS',
  'VIZ-BOOKS',
  'UDON-ENTERTAINMENT',
  'VERTICAL',
  'DARK-HORSE',
  'DARK-HORSE-MANGA',
  'SEVEN-SEAS',
  'SQUARE-ENIX-MANGA'
]

config = dotenv_values(".env")

MY_GUILD_NAME = 'Jake\'s Manga In-Stock Tracker (RightStufAnime)'

IN_STOCK_CHANNEL = 'in_stock'
OUT_OF_STOCK_CHANNEL = 'out_of_stock'
DAMAGED_AND_IMPERFECT_CHANNEL = 'damaged_and_imperfect'
PREORDERS_CHANNEL = 'preorders'
TEST_CHANNEL = 'testing_please_ignore'

guildChannelList = { 
  MY_GUILD_NAME : { 
    IN_STOCK_CHANNEL : {}, 
    OUT_OF_STOCK_CHANNEL: {}, 
    DAMAGED_AND_IMPERFECT_CHANNEL : {}, 
    PREORDERS_CHANNEL: {},
    TEST_CHANNEL : {}
  }   
}

async def doublePrint(channel, message):
  tries = 0
  while True:
    try:
      tries += 1
      if tries >= 3: 
        break
      await guildChannelList[MY_GUILD_NAME][channel].send(message)
      break
    except asyncio.CancelledError: 
      print('error posting to discord: [' + message + ']')
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
  if i['purchasable'] == True:
    global purchasable
    purchasable += 1
  i['url'] = 'https://www.rightstufanime.com/' + item['urlcomponent']
  i['found_on_url'] = foundURL
  if 'custitem_rs_new_releases_preorders' in item:
    if item['custitem_rs_new_releases_preorders'] == None or 'None' in item['custitem_rs_new_releases_preorders'] or 'New Release' in item['custitem_rs_new_releases_preorders']:
      i['preorder'] = False
    elif 'Pre-order' in item['custitem_rs_new_releases_preorders']:
      global preorders
      preorders += 1
      i['preorder'] = True  
    else: 
      print(item['custitem_rs_new_releases_preorders'])
      print('**********FUCKKKKK**************')
  else: 
    i['preorder'] = False
  if 'custitem_damaged_type' in item:
    if item['custitem_damaged_type'] == 'Imperfect':
      global imperfect  
      imperfect += 1
      i['imperfect'] = True
    else:
      i['imperfect'] = False
    if item['custitem_damaged_type'] == 'Damaged':
      global damaged
      damaged += 1
      i['damaged'] = True
    else:
      i['damaged'] = False

  i['last_checked'] = now.strftime(dateFormat)
  return i
###################################
  

###################################
async def runApp():
  global totalMismatches
  mismatches = 0
  preorderMismatch = 0
  inStockMismatch = 0
  outOfStockMismatch = 0
  damagedMismatch = 0
  imperfectMismatch = 0
  global damaged
  global imperfect
  global preorders
  global purchasable
  global itemsProcessed

  productCatalog = json.load( open( "right_stuf_anime.json" ) )

  with open("right_stuf_anime.on_start_backup.json", "w") as outfile:
    json.dump( productCatalog, outfile)

  for publisher in PUBLISHERS:
    publisherStartTime = datetime.datetime.now()
    page = 0
    itemsProcessedForPublisher = 0
    print(publisher)
    
    while True:
      url = makeRSURL(page, publisher)
      #print(url)
      ua = UserAgent()
      headers = {'User-Agent': ua.random}

      time.sleep(0.15)
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
      for item in items:
        time.sleep(0.14)
        i = processItem(item, url, now)
        itemsProcessed += 1
        itemsProcessedForPublisher += 1
        printProgressBar(itemsProcessedForPublisher, prefix = 'Progress:', suffix = str(itemsProcessedForPublisher), length = 50)
        if i['url'] in productCatalog:
          if 'damaged' in i and i['damaged'] and i['purchasable'] and not productCatalog[i['url']]['purchasable']:
            damagedMismatch +=1 
            changes = True
            await doublePrint(DAMAGED_AND_IMPERFECT_CHANNEL, '**[Damaged]** ' + i['name'] + '\n' + i['url'])
          elif 'imperfect' in i and i['imperfect'] and i['purchasable'] and not productCatalog[i['url']]['purchasable']:
            imperfectMismatch +=1
            changes = True
            await doublePrint(DAMAGED_AND_IMPERFECT_CHANNEL, '**[Imperfect]** ' + i['name'] + '\n' + i['url'])
          elif i['purchasable'] and productCatalog[i['url']]['preorder'] and not i['preorder']:
            mismatches += 1
            purchasableMismatch += 1
            changes = True
            await doublePrint(IN_STOCK_CHANNEL, '**[Preorder Now In Stock]** ' + i['name'] + '\n' + i['url'])
          elif productCatalog[i['url']]['purchasable'] and not i['purchasable'] and not productCatalog[i['url']]['preorder']:
            mismatches += 1
            outOfStockMismatch += 1
            changes = True
            await doublePrint(OUT_OF_STOCK_CHANNEL, '**[OUT OF STOCK]** ' + i['name'] + '\n' + i['url'])
          elif not productCatalog[i['url']]['purchasable'] and i['purchasable']:
            mismatches += 1
            inStockMismatch += 1
            changes = True
            await doublePrint(IN_STOCK_CHANNEL, '**[RESTOCK]** ' + i['name'] + '\n' + i['url'])    
        else:
          if i['preorder']:
            changes = True
            await doublePrint(PREORDERS_CHANNEL, '**[NEW]** ' + i['name'] + '\n' + i['url'])
          elif 'damaged' in i and i['damaged']:
            changes = True
            await doublePrint(DAMAGED_AND_IMPERFECT_CHANNEL, '**[Damaged]** ' + i['name'] + '\n' + i['url'])
          elif 'imperfect' in i and i['imperfect']:
            changes = True
            await doublePrint(DAMAGED_AND_IMPERFECT_CHANNEL, '**[Imperfect]** ' + i['name'] + '\n' + i['url'])
          elif i['purchasable']:
            changes = True
            await doublePrint(IN_STOCK_CHANNEL, '**[NEW]**' + i['name'] + '\n' + i['url'])
          else: 
            changes = True
            await doublePrint(OUT_OF_STOCK_CHANNEL, 'New Item scanned in out of stock: ' + i['name'] + '\n' + i['url'])

        productCatalog[i['url']] = i

      nextPageFound = False
      if 'links' in request.json():
        for item in request.json()['links']:
          if 'rel' in item:
            if item['rel'] == 'next':
                nextPageFound = True
                page += 1

      if changes:
        print('Dumping changes to disk...')
        with open("right_stuf_anime._change_dump_backup.json", 'w') as outfile:
          json.dump(productCatalog,  outfile)
        with open("right_stuf_anime.json", 'w') as outfile:
          json.dump(productCatalog,  outfile)

      if not nextPageFound: 
        print() 
        print('Last page: ' + str(page))
        break
    publisherEndTime = datetime.datetime.now()
    totalMismatches += mismatches
    print('------------------------------------------------')
    print('Publisher: ' + publisher)
    print('Mismatches This Scan: ' + str(mismatches))
    print('Total Session Mismatches: ' + str(totalMismatches))
    print('In Stock mismatches: ' + str(inStockMismatch))
    print('Out Of Stock mismatches: ' + str(outOfStockMismatch))
    print('Preorder Mismatches: ' + str(preorderMismatch))
    print('Damaged Mismatches: ' + str(damagedMismatch))
    print('Imperfect Mismatches: ' + str(imperfectMismatch))
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
  random.shuffle(PUBLISHERS)
  print(f'{client.user.name} has connected to Discord!')
  for guild in client.guilds:
    if guild.name in guildChannelList:
      print('[Guild]: ' + guild.name)
      for channel in guild.channels:
        if channel.name in guildChannelList[guild.name]:
          print('[Channel]: ' + channel.name)
          guildChannelList[guild.name][channel.name] = client.get_channel(channel.id)
  print('Publishers loaded:')
  for publisher in PUBLISHERS: 
    print(publisher)
  await doublePrint(TEST_CHANNEL, 'App booting up...')
  while True: 
    await runApp()

client.run(discordSecret)