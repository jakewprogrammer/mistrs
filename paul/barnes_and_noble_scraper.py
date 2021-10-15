import requests
from fake_useragent import UserAgent
import models
from bs4 import BeautifulSoup

BASE_URL = "https://www.barnesandnoble.com/b/_/"
MAX_PER_PAGE = 40


def ScrapeBarnesAndNoble(publisher):
    # prep request params
    page = 1  # page starts on 1
    headers = {"User-Agent": UserAgent().random}
    params = {
        'Ntt': publisher,
        'Ntk': 'Publisher',
        'Nrpp': MAX_PER_PAGE,
        'page': page,
    }

    # first request to get total page count
    request = requests.get(BASE_URL, headers=headers, params=params)
    if request.status_code != 200:
        print('request failed on {page}, exiting')
        return

    soup = BeautifulSoup(request.content, 'html.parser')

    # format is always "%d - %d of %d results", like "1 - 40 of 300 results"
    resultTxt = soup.find(class_='result-show').text
    total = (int)(resultTxt.split()[4])
    print(total)


if __name__ == "__main__":
    ScrapeBarnesAndNoble(models.PublisherNameHumanReadable[models.DARK_HORSE])