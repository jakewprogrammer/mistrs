from os import stat
import requests
import json
import time
import traceback
import random
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from torpy.http.requests import TorRequests

BASE_URL = "https://www.barnesandnoble.com"


viz_a_to_z = 'https://www.barnesandnoble.com/b/viz-media/_/N-1p70?Nrpp=40&Ns=P_Display_Name%7C0&page='
viz_z_to_a = "https://www.barnesandnoble.com/b/viz-media/_/N-1p70?Nrpp=40&Ns=P_Display_Name%7C1&page="

# kodansha_a_to_z = 'https://www.barnesandnoble.com/s/%22Kodansha+International%22?Nrpp=40&Ns=P_Display_Name%7C0&Ntk=Publisher&Ntx=mode+matchall&page='
# kodansha_z_to_a = 'https://www.barnesandnoble.com/s/%22Kodansha+International%22?&Ns=P_Display_Name%7C1&Ntk=Publisher&Ntx=mode+matchall&page='

yen_press_a_to_z = 'https://www.barnesandnoble.com/s/%22Yen+Press%22?Nrpp=40&Ns=P_Display_Name%7C0&Ntk=Publisher&Ntx=mode+matchall&page='
yen_press_z_to_a = 'https://www.barnesandnoble.com/s/%22Yen+Press%22?Nrpp=40&Ns=P_Display_Name%7C1&Ntk=Publisher&Ntx=mode+matchall&page='


URL_LIST = [
    yen_press_a_to_z,
    yen_press_z_to_a,
    viz_a_to_z,
    viz_z_to_a
]

MAX_PER_PAGE = 40

MAX_PAGE = 50
last_one = ""


productCatalog = json.load(open("b-and-n-2.json"))

with open("b-and-n-2.on_start_backup.json", "w") as outfile:
    json.dump(productCatalog, outfile,
              indent=4, sort_keys=True)


def ScrapeProductPage(productURL, product, sess, headers, state):
    time.sleep(0.1)

    # first request to get total page count
    request = sess.get(productURL, headers=headers, timeout=10)

    if request.status_code != 200:
        print(request.text)
        print(f'request failed on {productURL}, exiting')
        # every loop increments so reset state by decrementing by 1
        state['page'] -= 1
        raise Exception(str(request.status_code))

    soup = BeautifulSoup(request.content, 'html.parser')

    outOfStockNotice = soup.find('span', attrs={'class': 'notice'})
    inStockNotice = soup.find(
        'span', attrs={'class': 'shipping-message-text mt-0 mb-0'})

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


def ScrapeBarnesAndNoble(state, publisher, sess, headers):
    global last_one
    # prep request params
    page = 'page'
    local_last_one = ""
    while state[page] < 50:
        time.sleep(0.1)
        state[page] += 1
        # first request to get total page count
        currentURL = publisher+str(state[page])
        request = sess.get(currentURL, headers=headers, timeout=10)
        print(currentURL)
        if request.status_code != 200:
            print(request.text)
            print(f'request failed on {state[page]}, exiting')
            # every loop increments so reset state by decrementing by 1
            state[page] -= 1
            raise Exception(str(request.status_code))

        soup = BeautifulSoup(request.text, 'lxml')

        products = soup.find_all(
            class_='product-shelf-info product-info-view text--left pl-qa-s')

        random.shuffle(products)
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
                state[page] = 51
                break
            pJson['found-on'] = currentURL
            pJson['preorder'] = False
            pJson['in-stock'] = False

            print(url)
            format = product.find(class_='format').string.strip()
            bopis = product.find(
                class_='ml-xxs bopis-badge-message mt-0 mb-0')
            if format != 'Paperback':
                pJson['format'] = format
                pJson['on-nook'] = True
            elif bopis.string == 'Available Online':
                actuallyInStock = ScrapeProductPage(
                    url, pJson, sess, headers, state)
                print("Was actually in stock? : " +
                      str(actuallyInStock))
                pJson['in-stock'] = actuallyInStock
                if not actuallyInStock: 
                    pJson['bad-listing'] = True
            elif bopis.string == 'Pre-order Now':
                print("Preorder")
                pJson['preorder'] = True
            else:
                print("Out of stock")
            productCatalog[url] = pJson

        if state[page] % 20 == 0:
            with open("b-and-n-2.json", "w") as outfile:
                json.dump(productCatalog, outfile,
                          indent=4, sort_keys=True)

            # print(products)
        print(len(products))
        print('page: ' + str(state[page]))

        # format is always "%d - %d of %d results", like "1 - 40 of 300 results"
        resultTxt = soup.find(class_='result-show').text
        total = (int)(resultTxt.split()[4])
        print(total)
    with open("b-and-n-2.json", "w") as outfile:
        json.dump(productCatalog, outfile,
                  indent=4, sort_keys=True)

    print('ending run for publisher: ' + publisher)
    state[page] = 0
    if local_last_one != "":
        print('setting last one: ' + local_last_one)
        last_one = local_last_one


def Run():
    print("firing up the tor proxy")

    state = {}
    state['page'] = 0  # page starts on 1
    headers = {"User-Agent": UserAgent().random}
    while True:
        try:
            with TorRequests() as tor_requests:
                with tor_requests.get_session() as sess:
                    #print(sess.get("http://httpbin.org/ip", timeout=3).json())
                    request = sess.get(
                        'https://www.barnesandnoble.com/b/viz-media/_/N-1p70?Nrpp=40&Ns=P_Display_Name%7C0&page=1', headers=headers, timeout=6)

                    time.sleep(0.25)

                    print("Initial request: ")
                    print(request.text)
                    if request.status_code != 200:
                        print(
                            f'request failed on barnes and noble, getting new tor proxy')
                        continue

                    for publisher in URL_LIST:
                        ScrapeBarnesAndNoble(state, publisher, sess, headers)
        except Exception as e:
            print(e)
            print(traceback.format_exc())


if __name__ == "__main__":
    Run()
# ScrapeProductPage('https://www.barnesandnoble.com/w/oku-fumi-yoshinaga/1139704277')