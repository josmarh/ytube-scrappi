# -*- coding: utf-8 -*-
from __future__ import print_function # Python 2/3 compatibiltiy
from namedentities import *
from bs4 import BeautifulSoup
from random import randrange
import requests
import csv
import sys

proxies = []

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
    # f.writerow(['ip', 'port'])

    for item in proxy_list.select('tbody > tr'):
        try:
            f.writerow([item.select('td')[0].get_text(), item.select('td')[1].get_text()])
        except:
            print('')

def getRandomProxy():
    file = open('proxy.csv')

    csvreader = csv.reader(file)

    for item in csvreader:
        proxies.append(item)
    file.close()

    rnd=randrange(len(proxies))    
    proxy = {'ip': proxies[rnd][0], 'port': proxies[rnd][1]}

    return proxy

def scrapeYtube():
    proxy = getRandomProxy()
    proxies = {
        "http": f"https://{proxy['ip']}:{proxy['port']}",
        # "https": f"https://{proxy['ip']}:{proxy['port']}",
    }
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
    }

    vidIds = ["LRP8d7hhpoQ", "trW_lD9sBt0", "2NGjNQVbydc"]
    sortedIds = []
    isMonetizedStatus = ""

    for item in vidIds:
        try:
            r = requests.get("https://www.youtube.com/watch?v="+item, headers=header, proxies=proxies)
            html = repr(named_entities(r.content.decode("utf-8")))
            pos = html.find("getAdBreakUrl")

            if pos < 0:
                isMonetizedStatus = "NOT-MONETIZED"
            else:
                isMonetizedStatus = "MONETIZED"

            sortedIds.append({
                "vid": item,
                "status": isMonetizedStatus
            })
        except Exception as e:
            print(e)

    print(sortedIds) 


# LoadUpProxies()
# scrapeYtube()

# Reference: 
# https://proxiesapi.com/blog/biulding-a-simple-proxy-rotator-with-python-and-be.html.php
# https://github.com/rootVIII/proxy_requests
# https://stackoverflow.com/questions/51955795/python-proxy-requests-and-user-agent