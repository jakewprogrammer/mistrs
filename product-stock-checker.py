# Imports
from bs4 import BeautifulSoup
import requests
import json
import datetime
import time
import os
import re
import discord
import random
from discord.ext.commands import Bot
from discord.ext import commands
from datetime import timedelta
from ratelimit import limits
from dotenv import dotenv_values
from fake_useragent import UserAgent

# TODO: add ctrl-c handler save to disk
# TODO: fix backups schema to be less shitty lol
# TODO: flip flop logic for when caches are busting/less spam (can we update last message? mark it as flip flopping/inaccurate)
#       ^^^^^^^^ might be solved with double checker/better system anyways
# TODO: color console text
# TODO: better discord formatting

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

def checkRSURL(url):
  ua = UserAgent()
  headers = {'User-Agent': ua.random}

  tries = 0
  while True:
    try:
      time.sleep(2)
      request = requests.get(url, headers=headers)
      result  = BeautifulSoup(request.text,'lxml')
      serverStatus = request.status_code

      # If page is available
      if serverStatus == 200:
        # If item is in stock
        stockStatus = result.find('p', attrs={'class': 'product-line-stock-msg-in'})
        if stockStatus:
          return True
      else: 
        print(serverStatus)
      
      return False
    except:
      tries += 1
      print('Retrying single URL check for url: ' + url)
      if tries > 2:
        raise
         
async def doublePrint(channel, message):
  await guildChannelList[MY_GUILD_NAME][channel].send(message)
  print()
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
  if iteration%1000 == 0: 
    print()
  
  filledLength = int(length * (iteration%1000) // 1000)
  bar = fill * filledLength + '-' * (length - filledLength)
  print(f'\r{prefix} |{bar}| {suffix}', end = printEnd)
  # Print New Line on Complete

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

    random.shuffle(mangaListTargetURL)

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
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        response = requests.get(mangaURL, headers=headers)
        response.raise_for_status()
        return response

    repeats = 0
    totalProcessed = 0
    loopStartTime = datetime.datetime.now()
    print('Start time for loop: ' + loopStartTime.strftime(dateFormat)) 
    for mangaList in mangaListTargetURL:
      mangaURLList = [mangaList]
      totalThisList = 0
      publisherStartTime = datetime.datetime.now()
      print('Start time for publisher: ' + publisherStartTime.strftime(dateFormat))  
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
            time.sleep(3)

        result = BeautifulSoup(request.text,'lxml')
        #print(result)
        serverStatus = request.status_code
        changes = False
        if serverStatus == 200:
          mangaList = result.find_all('div', attrs={'class': 'facets-item-cell-grid'})
          
          # page loaded with error
          if len(mangaList) == 0 and repeats < 1:
            mangaURLList.append(mangaURL)
            repeats += 1
            print()
            print('Retrying url (time: ' + str(repeats) + '): ' + mangaURL)
          else: 
            repeats = 0
        
          for mangaBook in mangaList:
            totalThisList += 1
            totalThisLoop += 1
            printProgressBar(totalThisList, prefix = 'Progress:', suffix = str(totalThisList), length = 50)
            
            wasInStock = False
            wasPreorderable = False
            wasPreviouslyScanned = False
            imperfect = False
            damaged = False

            stockJSON = {}
            url = 'https://www.rightstufanime.com' + mangaBook.find('a', attrs={'class':'facets-item-cell-grid-link-image'})['href']
            
            if url in targetStockMap:
              # deep copy this to make modifications to that we might throw out
              stockJSON = dict(targetStockMap[url])
              wasPreviouslyScanned = True
              if targetStockMap[url]['purchasable'] == True:
                wasInStock = True
              if targetStockMap[url]['preorder'] == True:
                wasPreorderable = True
                        
            altText = mangaBook.find('img', attrs={'class':'facets-item-cell-grid-image'})['alt']
            stockJSON['title'] = altText
            
            if '[Imperfect]' in altText:
              imperfect = True
              stockJSON['imperfect'] = True
            if '[Damaged]' in altText:
              damaged = True
              stockJSON['damaged'] = True
            
            stockJSON['url'] = url
            stockJSON['found_on_url'] = mangaURL 

            stockStatus = mangaBook.find('p', attrs={'class': 'product-line-stock-msg-in'} )
            preorderStatus = mangaBook.find('p', attrs={'class': 'product-line-stock-msg-pre-order'})
            
            try:
              now = datetime.datetime.now()     
              if stockStatus:
                stockJSON['purchasable'] = True
                stockJSON['preorder'] = False
                stockJSON['last_checked'] = now.strftime(dateFormat)
                if (not wasInStock or wasPreorderable):
                  if 'status_change_time' in stockJSON:
                    oldTime = stockJSON['status_change_time'] 
                    difference = now - oldTime
                    #TODO 
                    # if difference < thresholdTime
                    #   edit post
                  stockJSON['status_change_time'] = now.strftime(dateFormat)

                if imperfect and (not wasPreviouslyScanned or not wasInStock):
                  changes = True
                  await doublePrint(DAMAGED_AND_IMPERFECT_CHANNEL, '**[Damaged]** ' + altText + '\n' + url)
                elif damaged and (not wasPreviouslyScanned or not wasInStock):
                  changes = True  
                  await doublePrint(DAMAGED_AND_IMPERFECT_CHANNEL, '**[Imperfect]** ' + altText + '\n' + url)
                elif wasPreorderable:
                  changes = True
                  await doublePrint(IN_STOCK_CHANNEL, '**[Preorder Now In Stock]** ' + altText + '\n' + url)
                elif not wasPreviouslyScanned: 
                  changes = True
                  await doublePrint(IN_STOCK_CHANNEL, '**[NEW]**' + altText + '\n' + url)
                elif not wasInStock:
                  ### we get a bunch of false positives sometimes that doesn't hurt to check
                  doubleCheckIsInStock = checkRSURL(url)
                  totalRequests += 1
                  if not doubleCheckIsInStock:
                    await doublePrint(TEST_CHANNEL, "Skipping bad restock for book: " + altText + '\n' + url)
                    print(mangaURL)
                    continue
                  changes = True
                  await doublePrint(IN_STOCK_CHANNEL, '**[RESTOCK]** ' + altText + '\n' + url)
                  
              elif preorderStatus:
                stockJSON['purchasable'] = True
                stockJSON['preorder'] = True
                stockJSON['last_checked'] = now.strftime(dateFormat)
                if not wasPreorderable:
                  changes = True
                  await doublePrint(PREORDERS_CHANNEL, '**[NEW]** ' + altText + '\n' + url)
              else:
                stockJSON['purchasable'] = False
                stockJSON['preorder'] = False
                stockJSON['last_checked'] = now.strftime(dateFormat)
                if wasInStock:
                  isInStock = checkRSURL(url)
                  totalRequests += 1
                  if isInStock:
                    await doublePrint(TEST_CHANNEL, "Skipping bad out of stock for book: " + altText + '\n' + url)
                    print(mangaURL)
                    continue 
                  changes = True
                  await doublePrint(OUT_OF_STOCK_CHANNEL, '**[OUT OF STOCK]** ' + altText + '\n' + url)
                  print(mangaURL)
                  for book in mangaList:
                    print(book.find('img', attrs={'class':'facets-item-cell-grid-image'})['alt'])
                elif not wasPreviouslyScanned:
                  changes = True 
                  await doublePrint(OUT_OF_STOCK_CHANNEL, "New Item scanned in out of stock: " + altText + '\n' + url)
            except:
              print()
              print("Unexpected error for book: " + altText)
              doublePrint(TEST_CHANNEL, 'Check logs for caught exception.')

            targetStockMap[url] = stockJSON

        else: 
          print()
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
                print()
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
          print()
          print("Total this loop: " + str(totalThisLoop))
          print("Total processed: " + str(totalProcessed))
          print('Total RS Web Requests: ' + str(totalRequests))
          print('\n')    

      publisherEndTime = datetime.datetime.now()
      print()
      print('End time for publisher: ' + publisherEndTime.strftime(dateFormat))
      print('Total time: ' + str(publisherEndTime-publisherStartTime))   
      print('Total scraped: ' + str(totalThisList))
      print()
      json.dump( targetStockMap, open( "file_name.json", 'w' ) )

    loopEndTime = datetime.datetime.now()
    print('End time for loop: ' + loopEndTime.strftime(dateFormat))
    print('Total time: ' + str(loopEndTime-loopStartTime))
    print('\n')   
    print('Total Requests: ' +   str(totalRequests))
    print("Total processed: " + str(totalProcessed))
    print('----------------------------------------------------')
    await doublePrint(TEST_CHANNEL, "Loop done")


client = discord.Client()

discordSecret = config['TOKEN']

@client.event
async def on_ready():
  print(f'{client.user.name} has connected to Discord!')
  for guild in client.guilds:
    if guild.name in guildChannelList:
      print('[Guild]: ' + guild.name)
      for channel in guild.channels:
        if channel.name in guildChannelList[guild.name]:
          print('[Channel]: ' + channel.name)
          guildChannelList[guild.name][channel.name] = client.get_channel(channel.id)

  await doublePrint(TEST_CHANNEL, 'App booting up...')
  await runApp()


client.run(discordSecret)
# This would enable the bot command code vs the client we're using atm
# bot.run(discordSecret)