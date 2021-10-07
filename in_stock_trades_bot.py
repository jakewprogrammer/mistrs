import requests
import time
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


publishersList = [
    'https://www.instocktrades.com/publishers/viz-media?pg='
]

productCatalog = {}

for publisherURL in publishersList:
    page = 0
    while True:
        page += 1
        targetURL = publisherURL + str(page)
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        request = requests.get(targetURL, headers=headers)
        result  = BeautifulSoup(request.text,'lxml')
        serverStatus = request.status_code

        # If page is available
        if serverStatus == 200:
            stockStatus = result.find_all("div", attrs={"class": "item thumbplus"})
            itemsfound = 0
            for item in stockStatus:
                time.sleep(0.3)
                itemsfound += 1
                manga = item.find("div", attrs={"class": "title"})

                link = 'https://www.instocktrades.com/' + manga.find("a")['href']
                print(link)
                mangaName = manga.find("a").string
                print(mangaName)

                mangaDesc = item.find("div", attrs={"class": "shortdesc desc"})
                print(mangaDesc.string.strip())

                mangaPrice = item.find("div", attrs={"class": "price"})
                
                print(mangaPrice.string.strip())

                productCatalog[link] = {
                    'url': link,
                    #'desc': mangaDesc,
                    'price': mangaPrice,
                    'name': mangaName
                }
                

            if itemsfound == 0:
                print("exit")
                break
        else: 
            print("Error loading page")
      