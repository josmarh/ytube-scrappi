import csv
from random import randrange

proxies = []

def getRandomProxy():
    file = open('proxy.csv')

    csvreader = csv.reader(file)

    for item in csvreader:
        proxies.append(item)
    file.close()

    rnd=randrange(len(proxies))    
    proxy = {'ip': proxies[rnd][0], 'port': proxies[rnd][1]}

    return proxy