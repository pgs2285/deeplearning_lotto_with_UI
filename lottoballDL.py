import os
import urllib.request
url ='http://xn--961bo7bu9e22au6jgo2b.xn--6w6btr.kr/cbimg/'

for i in range(1,46):

    num = f'{i}.gif'
    site = url+num

    # urllib.requests.get(site, headers={ "User-Agent": "Mozilla/5.0" })
    urllib.request.urlretrieve(site, f"./ball_photo/{i}.gif")

