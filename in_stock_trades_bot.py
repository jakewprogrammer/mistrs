from bs4 import BeautifulSoup
import requests
import time


publishersList = [
    'https://www.instocktrades.com/publishers/viz-media?pg='
]


for publisherURL in publishersList:
    page = 0
    
    while True:
        page += 1
        targetURL = publisherURL + str(page)
        request = requests.get(targetURL)
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
                print(manga.find("a").string) 

                mangaDesc = item.find("div", attrs={"class": "shortdesc desc"})
                print(mangaDesc.string.strip())

                mangaPrice = item.find("div", attrs={"class": "price"})
                
                print(mangaPrice.string.strip())
                

            if itemsfound == 0:
                print("exit")
                break
        else: 
            print("Error loading page")
      