from os import replace
import requests
import json
import time
import datetime
import asyncio
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

KODANSHA = 'KODANSHA-COMICS'
YEN_PRESS = 'YEN-PRESS'
VIZ = 'VIZ-BOOKS'
UDON = 'UDON-ENTERTAINMENT'
VERTICAL = 'VERTICAL'
DARK_HORSE = 'DARK-HORSE'
DARK_HORSE_MANGA = 'DARK-HORSE-MANGA'
SEVEN_SEAS = 'SEVEN-SEAS'

# will have an out of stock bug ATM if two on the list share the same publisher
publishersList = {
    'https://www.instocktrades.com/publishers/yen-press?pg=' : YEN_PRESS,
    'https://www.instocktrades.com/publishers/dark-horse?pg=' : DARK_HORSE,
    'https://www.instocktrades.com/publishers/viz-media?pg=' : VIZ, 
    'https://www.instocktrades.com/publishers/vertical?pg=' : VERTICAL,
    'https://www.instocktrades.com/publishers/seven-seas-entertainment?pg=' : SEVEN_SEAS,
    'https://www.instocktrades.com/publishers/udon-entertainment?pg=' :  UDON,
    'https://www.instocktrades.com/publishers/kodansha?pg=' : KODANSHA,
}
    
dateFormat = '%b %d %Y %I:%M%p'

#for testing/backfilling
def compareItemAndPublishMessage(i, productCatalog, now, mDict, publisher, category, itemsProcessedForPublisher, discordChannelMentionMap):
  changes = False
  url = i['url']
  nameAndURL = i['name'] + '\n' + url
  if url in productCatalog:
    if 'damaged' in i and i['damaged'] and i['purchasable'] and not productCatalog[url]['purchasable']:
      mDict['damagedMismatch'] +=1 
      changes = True
      
      print('**[Damaged]**\n' + nameAndURL)
    elif 'imperfect' in i and i['imperfect'] and i['purchasable'] and not productCatalog[url]['purchasable']:
      mDict['imperfectMismatch'] +=1
      changes = True
      print('**[Damaged]**\n' + nameAndURL)
    elif i['purchasable'] and productCatalog[url]['preorder'] and not i['preorder']:
      mDict['mismatches'] += 1
      mDict['preorderMismatch'] += 1
      changes = True
      print('**[Preorder in stock]**\n' + nameAndURL)
    elif productCatalog[url]['purchasable'] and not i['purchasable'] and not productCatalog[url]['preorder']:
      mDict['mismatches'] += 1
      mDict['outOfStockMismatch'] += 1
      changes = True
      print('**[Out of stock]**\n' + nameAndURL)
    elif not productCatalog[url]['purchasable'] and i['purchasable']:
      mDict['mismatches'] += 1
      mDict['inStockMismatch'] += 1
      changes = True
      print('**[Restock]**\n' + nameAndURL)
  else:
    if i['preorder']:
      changes = True

      print('**[pre]**\n' + nameAndURL)
    elif 'damaged' in i and i['damaged']:
      changes = True

      print('**[dammmm]**\n' + nameAndURL)
    elif 'imperfect' in i and i['imperfect']:
      changes = True

    elif i['purchasable']:
      changes = True

      print('**[New scan]**\n' + nameAndURL)
    else: 
      changes = True

      print('**[should never happen]**\n' + nameAndURL)
  return changes

async def scanInStockTrades(compareItemAndPublishMessage, mDict, DiscordChannelToMentionMap):
    productCatalog = json.load( open( "in_stock_trades_fixed.json" ) )
    with open("in_stock_trades_fixed.on_start_backup.json", "w") as outfile:
        json.dump( productCatalog, outfile) 
        
    productCatalogOld = dict(productCatalog)
    for publisherURL in publishersList.keys():
        print(publishersList[publisherURL])
        totalItems = 0
        page = 0
        
        while True:
            now = datetime.datetime.now()
            page += 1
            targetURL = publisherURL + str(page)
            ua = UserAgent()
            headers = {'User-Agent': ua.random}
            request = requests.get(targetURL, headers=headers)
            await asyncio.sleep(0.5)
            #time.sleep(0.05)
            result  = BeautifulSoup(request.text,'lxml')
            serverStatus = request.status_code

            # If page is available
            if serverStatus == 200:
                stockStatus = result.find_all("div", attrs={"class": "item thumbplus"})
                itemsfound = 0
                changes = False
                for item in stockStatus:
                    #time.sleep(0.3)
                    itemsfound += 1
                    totalItems += 1
                    manga = item.find("div", attrs={"class": "title"})

                    link = 'https://www.instocktrades.com' + manga.find("a")['href']
                    mangaName = manga.find("a").string
                    category = 'Manga'
                    if 'Light Novel' in mangaName:
                        mangaName.replace('Light Novel', '')
                        category = 'Novels'
                    if ' GN ' in mangaName:
                        # pray the name of this graphic novel isnt REIGN GN vol 1 etc
                        mangaName.replace('GN ', '')

                    #print(mangaName)

                    mangaDesc = item.find("div", attrs={"class": "shortdesc desc"})
                    #print(mangaDesc.string.strip())

                    mangaPrice = item.find("div", attrs={"class": "price"}).string.strip()

                    mangaIsDamaged = item.find("div", attrs={"class": "damage"})
                    damaged = False
                    if mangaIsDamaged:
                        damaged = True
                    
                    publisher = publishersList[publisherURL]
                    #print(mangaPrice.string.strip())

                    i = {
                        'url': link,
                        #'desc': mangaDesc,
                        'price': mangaPrice,
                        'name': mangaName,
                        'damaged': damaged,
                        'imperfect': False,
                        'preorder': False,
                        'purchasable': True,
                        'category': category,
                        'publisher': publisher,
                        'found_on_url': link,
                        'last_checked': now.strftime(dateFormat),
                    }
                    
                    changes = await compareItemAndPublishMessage(i, productCatalog, now, mDict, publisher, category, totalItems, DiscordChannelToMentionMap)
                    #changes = compareItemAndPublishMessage(i, productCatalog, now, mDict, publisher, category, totalItems, DiscordChannelToMentionMap)
                    productCatalog[link] = i

                    productCatalogOld.pop(link, None)
                    #print(productCatalog[link])

                if changes:
                    with open("in_stock_trades.json", 'w') as outfile:
                        json.dump(productCatalog,  outfile)    

                if itemsfound == 0:
                    print("exit")
                    break
            else: 
                print("Error loading page")
        
        changes = False
        # go through every link not in the latest download
        for link in productCatalogOld.keys():
            i = dict(productCatalog[link])
            # skip items that wouldn't be in this query
            if productCatalogOld[link]['publisher'] != publishersList[publisherURL]:
                continue
            totalItems +=1
            i['last_checked'] = now.strftime(dateFormat)
            i['purchasable'] = False

            changes = await compareItemAndPublishMessage(i, productCatalog, now, mDict, publisher, category, totalItems, DiscordChannelToMentionMap)
            #changes = compareItemAndPublishMessage(i, productCatalog, now, mDict, publisher, category, totalItems, DiscordChannelToMentionMap)
            productCatalog[link] = i
        if changes:
            with open("in_stock_trades_fixed.changes_backup.json", 'w') as outfile:
                json.dump(productCatalog,  outfile)
            with open("in_stock_trades_fixed.json", 'w') as outfile:
                json.dump(productCatalog,  outfile)    


    with open("in_stock_trades_fixed.final_dump.json", 'w') as outfile:
        json.dump(productCatalog,  outfile)
    with open("in_stock_trades_fixed.json", 'w') as outfile:
        json.dump(productCatalog,  outfile)
        
#def noOpCompare(*args):
#    return
    
#scanInStockTrades(compareItemAndPublishMessage, {}, {})