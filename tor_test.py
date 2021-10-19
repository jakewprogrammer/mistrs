from torpy.http.requests import TorRequests
from fake_useragent import UserAgent
ua = UserAgent()
headers = {'User-Agent': ua.random}

with TorRequests() as tor_requests:
    print("build circuit")
    with tor_requests.get_session() as sess:
        print(sess.get("http://httpbin.org/ip").json())
        print(sess.get("http://httpbin.org/ip").json())
        print(sess.get('https://www.barnesandnoble.com/b/viz-media/_/N-1p70?Nrpp=40&Ns=P_Display_Name%7C0&page=1',
              headers=headers, timeout=10).text)
    print("renew circuit")
    with tor_requests.get_session() as sess:
        print(sess.get("http://httpbin.org/ip").json())
        print(sess.get("http://httpbin.org/ip").json())
        print(sess.get('https://www.barnesandnoble.com/b/viz-media/_/N-1p70?Nrpp=40&Ns=P_Display_Name%7C0&page=1',
              headers=headers, timeout=10).text)
