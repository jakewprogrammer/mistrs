# Imports
from bs4 import BeautifulSoup
import requests
import json
import datetime
import time
import os
import re
import discord
from discord.ext.commands import Bot
from discord.ext import commands
from datetime import timedelta
from ratelimit import limits
from dotenv import dotenv_values

config = dotenv_values(".env")

MY_GUILD_NAME = 'Jake\'s Manga In-Stock Tracker (RightStufAnime)'

guildChannelList = { 
  'Jake\'s Manga In-Stock Tracker (RightStufAnime)' : { 
    'in_stock' : {}, 
    'out_of_stock': {}, 
    'damaged_and_imperfect' : {}, 
    'preorders': {},
    'testing_please_ignore' : {}
  }   
}

IN_STOCK_CHANNEL = 'in_stock'
OUT_OF_STOCK_CHANNEL = 'out_of_stock'
DAMAGED_AND_IMPERFECT_CHANNEL = 'damaged_and_imperfect'
PREORDERS_CHANNEL = 'preorders'
TEST_CHANNEL = 'testing_please_ignore'

async def doublePrint(channel, message):
  await guildChannelList[MY_GUILD_NAME][channel].send(message)
  print(message)

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
    percent = ("{0:." + str(decimals) + "f}").format(100 * ((iteration%1000) / float(1000)))
    filledLength = int(length * (iteration%1000) // 1000)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration%999 == 0: 
        print()

async def runApp():
  while True:
    # Target URL's
    targetURLs = []

    mangaListTargetURL = [
      'https://www.rightstufanime.com/category/Manga/publisher/VIZ-BOOKS',
      'https://www.rightstufanime.com/category/Manga/publisher/UDON-ENTERTAINMENT',
      'https://www.rightstufanime.com/category/Manga/publisher/VERTICAL',
      'https://www.rightstufanime.com/category/Manga/publisher/YEN-PRESS',
      'https://www.rightstufanime.com/category/Manga/publisher/DARK-HORSE',
      'https://www.rightstufanime.com/category/Manga/publisher/DARK-HORSE-MANGA',
      'https://www.rightstufanime.com/category/Manga/publisher/KODANSHA-COMICS',
      'https://www.rightstufanime.com/category/Manga/publisher/SEVEN-SEAS',
      'https://www.rightstufanime.com/category/Manga/publisher/SQUARE-ENIX-MANGA'
      # mega query
      #'https://www.rightstufanime.com/category/Manga/publisher/DARK-HORSE,DARK-HORSE-MANGA,KODANSHA,KODANSHA-COMICS,SEVEN-SEAS,SQUARE-ENIX-MANGA,UDON-ENTERTAINMENT,VERTICAL,VIZ-BOOKS,YEN-PRESS?show=96&page=1'
      #'https://www.rightstufanime.com/category/Manga'
      #'https://www.rightstufanime.com/category/Manga?page=194'
      #'https://www.rightstufanime.com/search?keywords=vagabond',
    ]

    dateFormat = '%b %d %Y %I:%M%p' 
    targetStockMap = json.load( open( "file_name.json" ) )

    i = 0
    while os.path.exists("file_name.%s.json_backup" % i):
        i += 1

    with open("file_name.%s.json_backup" % i, "w") as outfile:
      json.dump( targetStockMap, outfile)
    
    totalRequests = 0

    time_change = datetime.timedelta(hours=24)

    @limits(calls=1, period=timedelta(seconds=1).total_seconds())
    def get_response(url):
        response = requests.get(mangaURL)
        response.raise_for_status()
        return response

    repeats = 0
    totalProcessed = 0

    for mangaList in mangaListTargetURL:
      mangaURLList = [mangaList]
      totalThisList = 0
      print(mangaURLList)
      print('\n')
      for mangaURL in mangaURLList:
        totalThisLoop = 0
        totalRequests += 1
        request = {}
        while True:
          try:
            request = get_response(mangaURL)
            break;
          except:
            time.sleep(2)

        result = BeautifulSoup(request.text,'lxml')
        #print(result)
        serverStatus = request.status_code
        changes = False
        if serverStatus == 200:
          mangaList = result.find_all('div', attrs={'class': 'facets-item-cell-grid'})
          
          if len(mangaList) == 0 and repeats < 1:
            mangaURLList.append(mangaURL)
            repeats += 1
            print('Retrying url (time: ' + str(repeats) + '): ' + mangaURL)
          else: 
            repeats = 0
        
          for mangaBook in mangaList:
            totalThisList += 1
            totalThisLoop += 1
            printProgressBar(totalThisList + 1, prefix = 'Progress:', suffix = str(totalThisList), length = 50)
            stockJSON = {}
            altText = mangaBook.find('img', attrs={'class':'facets-item-cell-grid-image'})['alt']
            stockJSON['title'] = altText
            imperfect = False
            damaged = False
            if '[Imperfect]' in altText:
              imperfect = True
              stockJSON['imperfect'] = True
            if '[Damaged]' in altText:
              damaged = True
              stockJSON['damaged'] = True
            url = 'https://www.rightstufanime.com' + mangaBook.find('a', attrs={'class':'facets-item-cell-grid-link-image'})['href']
            stockJSON['url'] = url
            stockJSON['found_on_url'] = mangaURL 

            stockStatus = mangaBook.find('p', attrs={'class': 'product-line-stock-msg-in'} )
            preorderStatus = mangaBook.find('p', attrs={'class': 'product-line-stock-msg-pre-order'})

            wasInStock = False
            wasPreorderable = False
            wasPreviouslyScanned = False

            if url in targetStockMap:
              wasPreviouslyScanned = True
              if targetStockMap[url]['purchasable'] == True:
                wasInStock = True
              if targetStockMap[url]['preorder'] == True:
                wasPreorderable = True
              
              try:
                now = datetime.datetime.now()    	
                if stockStatus:
                  stockJSON['purchasable'] = True
                  stockJSON['preorder'] = False
                  stockJSON['last_checked'] = now.strftime(dateFormat)
                  if imperfect and (not wasPreviouslyScanned or not wasInStock):
                    changes = True
                    await doublePrint(DAMAGED_AND_IMPERFECT_CHANNEL, 'Damaged copy for sale\n' + altText + '\n' + url)
                  elif damaged and (not wasPreviouslyScanned or not wasInStock):
                    changes = True  
                    await doublePrint(DAMAGED_AND_IMPERFECT_CHANNEL, 'Imperfect copy for sale\n' + altText + '\n' + url)
                  elif wasPreorderable:
                    changes = True
                    await doublePrint(IN_STOCK_CHANNEL, 'Preorderable item now for sale!!!\n' + altText + '\n' + url)
                  elif not wasPreviouslyScanned: 
                    changes = True
                    await doublePrint(IN_STOCK_CHANNEL, 'First time seeing item in stock!!!\n' + altText + '\n' + url)
                  elif not wasInStock:
                    changes = True
                    await doublePrint(IN_STOCK_CHANNEL, 'New Item *back* in stock!!!\n' + altText + '\n' + url)
                elif preorderStatus:
                  stockJSON['purchasable'] = True
                  stockJSON['preorder'] = True
                  stockJSON['last_checked'] = now.strftime(dateFormat)
                  if not wasPreorderable:
                    changes = True
                    await doublePrint(PREORDERS_CHANNEL, 'New preordable item!\n' + altText + '\n' + url)
                else:
                  stockJSON['purchasable'] = False
                  stockJSON['preorder'] = False
                  stockJSON['last_checked'] = now.strftime(dateFormat)
                  if wasInStock: 
                    changes = True
                    await doublePrint(OUT_OF_STOCK_CHANNEL, 'Item just went out of stock!!\n' + altText + '\n' + url)
                  elif not wasPreviouslyScanned:
                    changes = True 
                    await doublePrint(OUT_OF_STOCK_CHANNEL, "New Item scanned in out of stock!\n" + altText + '\n' + url)
              except:
                print("Unexpected error for book: " + altText)
                doublePrint(TEST_CHANNEL, 'Check logs for caught exception.')

              targetStockMap[url] = stockJSON

        else: 
          print(serverStatus)
          print(request)

        if changes:
          with open( "file_name.json", 'w' ) as outfile:
            json.dump( targetStockMap,  outfile)
          
        nextLinkList = result.find_all('li', attrs={'class': 'global-views-pagination-next'})
        for nextLink in nextLinkList :
            nextLinkHRF = nextLink.find('a', attrs={'title': 'Next page'})
            if nextLinkHRF['href'] != mangaURL:
              nextLinkAppend = nextLinkHRF['href']

              nextLinkActual = ''
              if nextLinkAppend == '#':
                print("constructing new page url")
                m = re.search(r'\d+$', mangaURL)
                if m is not None:
                  newPage = int(m.group()) + 1
                  urlConstruction = mangaURL.split('page=')
                  nextLinkActual = urlConstruction[0] + 'page=' + str(newPage)
              else:
                nextLinkActual = 'https://www.rightstufanime.com'+ nextLinkAppend
              #print(nextLinkActual)
              mangaURLList.append(nextLinkActual)

        totalProcessed += totalThisLoop
        if totalRequests % 100 == 0:
          with open( "file_name.json", 'w' ) as outfile:
            json.dump( targetStockMap,  outfile)
          print('\n')
          print("Total this loop: " + str(totalThisLoop))
          print("Total processed: " + str(totalProcessed))
          print('Total RS Web Requests: ' + str(totalRequests))
          print('\n')    

    json.dump( targetStockMap, open( "file_name.json", 'w' ) )
    print('\n')   
    print('Total Requests: ' +   str(totalRequests))
    print("Total processed: " + str(totalProcessed))
    print('----------------------------------------------------')


client = discord.Client()

discordSecret = config['TOKEN']
bot = commands.Bot(command_prefix='!')

@bot.command(name='create-channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)



@client.event
async def on_ready():
  print(f'{client.user.name} has connected to Discord!')
  for guild in client.guilds:
    if guild.name in guildChannelList:
      print(guild.name)
      for channel in guild.channels:
        if channel.name in guildChannelList[guild.name]:
          print(channel.name)
          guildChannelList[guild.name][channel.name] = client.get_channel(channel.id)

  await doublePrint(TEST_CHANNEL, 'App booting up...')
  await runApp()

client.run(discordSecret)