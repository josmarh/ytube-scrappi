#!/usr/bin/python

# Description: Scrape world timezones data from https://timezonedb.com/time-zones

from bs4 import BeautifulSoup
import requests
import csv

TIMEZONE_URL='https://timezonedb.com'

# Collect page data 
page = requests.get(TIMEZONE_URL+'/time-zones')
# Create a BeautifulSoup object
soup = BeautifulSoup(page.text, 'html.parser')

# Pull all text from the table
timezone_list = soup.find_all('table')[0]
# Pull td from all instances of <tr> tag within BodyText div
timezone_data_list_items = timezone_list.select('tbody > tr')

# Create a file to write to, add headers row
f = csv.writer(open('timezonedb.csv', 'w'))
f.writerow(['country_code','country_name','time_zone','gmt_offset','timezone_link'])

for timezone_data in timezone_data_list_items[0:]:
    timezones = []
    for th in timezone_data.find_all('td'):
        timezones.append(th.text.rstrip())
        th_link = timezone_data.find_all('td')[2].find('a')
    timezones.append(TIMEZONE_URL+th_link['href'])
    f.writerow(timezones)
