import requests
import json
import time
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

BASE_URL = "https://www.barnesandnoble.com"


a_to_z = 'https://www.barnesandnoble.com/b/viz-media/_/N-1p70?Nrpp=40&Ns=P_Display_Name%7C0&page='
z_to_a = "https://www.barnesandnoble.com/b/viz-media/_/N-1p70?Nrpp=40&Ns=P_Display_Name%7C1&page="

URL_LIST = [
    a_to_z
]

MAX_PER_PAGE = 40

MAX_PAGE = 50
last_one = ""

productCatalog = {}

def ScrapeProductPage(productURL, product):
    time.sleep(0.1)
    headers = {"User-Agent": UserAgent().random}

    # first request to get total page count
    request = requests.get(productURL, headers=headers)

    if request.status_code != 200:
        print('request failed on {page}, exiting')
        return

    soup = BeautifulSoup(request.content, 'html.parser')

    outOfStockNotice = soup.find('span', attrs={'class':'notice'})
    inStockNotice = soup.find('span', attrs={'class':'shipping-message-text mt-0 mb-0'})

    if outOfStockNotice:
        print("out of stock notice")
        print(outOfStockNotice.string)
        product['out-of-stock-notice'] = outOfStockNotice.string
        return False
    elif inStockNotice:
        print("in stock notice")
        print(inStockNotice)
        product['in-stock-notice'] = inStockNotice.string
        return True
    else:
        print("probably out of stock")
        return False
    

def ScrapeBarnesAndNoble(publisher):
    global last_one
    # prep request params
    page = 0  # page starts on 1
    headers = {"User-Agent": UserAgent().random}

    while page <= 50:
        time.sleep(0.1)
        page += 1
        # first request to get total page count
        currentURL = publisher+str(page)
        request = requests.get(currentURL, headers=headers)
        print(currentURL)
        if request.status_code != 200:
            print('request failed on {page}, exiting')
            return

        soup = BeautifulSoup(request.content, 'html.parser')

        products = soup.find_all(class_='product-shelf-info product-info-view text--left pl-qa-s')
        local_last_one = ""
        for product in products:
            pJson = {}
            
            a = product.find('a')
            url = BASE_URL+a['href'].partition(';')[0]
            pJson['name'] = a['title']
            pJson['url'] = url
            local_last_one = url
            if local_last_one == last_one:
                print('last one found: ' + last_one)
                local_last_one = ""
                last_one = ""
                page = 51
                break
            pJson['found-on'] = currentURL
            pJson['preorder'] = False
            pJson['in-stock'] = False
            
            print(url)
            format = product.find(class_='format').string.strip()
            bopis = product.find(class_='ml-xxs bopis-badge-message mt-0 mb-0')
            if format.strip() != 'Paperback':
                print(format + ' should be Nook detected, out of stock assumed')
                pJson['on-nook'] = True
            elif bopis.string == 'Available Online':
                print("In stock detected")
                actuallyInStock = ScrapeProductPage(url, pJson)
                print("Was actually in stock? : " + str(actuallyInStock))
                pJson['in-stock'] = actuallyInStock
            elif bopis.string == 'Pre-order Now':
                print("Preorder")
                pJson['preorder'] = True
            else: 
                print("Out of stock")      
            productCatalog[url] = pJson
            
        if local_last_one != "": 
            last_one = local_last_one

        with open("b-and-n-2.json", "w") as outfile:
            json.dump( productCatalog, outfile, indent=4, sort_keys=True) 
            #print(products)
        print(len(products))
        print('page: ' + page)

        # format is always "%d - %d of %d results", like "1 - 40 of 300 results"
        resultTxt = soup.find(class_='result-show').text
        total = (int)(resultTxt.split()[4])
        print(total)

def Run():
    for publisher in URL_LIST:
        ScrapeBarnesAndNoble(publisher)

Run()
#ScrapeProductPage('https://www.barnesandnoble.com/w/oku-fumi-yoshinaga/1139704277')