# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import csv

def LoadUpProxies():
    url='https://sslproxies.org'

    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
    }

    response=requests.get(url,headers=header)

    soup=BeautifulSoup(response.content, 'lxml')

    proxy_list = soup.find_all('table')[0]

    # Create a file to write to, add headers row
    f = csv.writer(open('proxy.csv', 'w', newline=''))

    for item in proxy_list.select('tbody > tr'):
        try:
            f.writerow([item.select('td')[0].get_text(), item.select('td')[1].get_text()])
        except:
            print('')


LoadUpProxies()