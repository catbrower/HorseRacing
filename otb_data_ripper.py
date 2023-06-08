import json
import scrapy
import requests
from bson import ObjectId
from datetime import datetime
from pymongo import MongoClient

# Probably not gonna use this, I just realized you can directly hit the endpoints
class OTBSpider(scrapy.Spider):
    name = 'otbspider'
    start_urls = ['https://www.offtrackbetting.com/results/82/saratoga-%28tb%29-20110722.html']

    def parse(self, response):
        xpath_title = '/html/body/div[2]/div[2]/div/div[1]/div[1]/h1/text()'
        title_parts = [x.strip() for x in response.xpath(xpath_title).get().split('-')]
        title_parts[0] = title_parts[0].replace('Results', '').strip()
        title_parts[1] = datetime.strptime(title_parts[1], '%B %d, %Y')
        yield title_parts[0]
        yield title_parts[1]

        # Get race results
        xpath_races = '/html/body/div[2]/div[2]/div/div[1]/div[5]/div'

client = MongoClient('mongodb://localhost:27017')
collection = client['horse_racing']['races']

start_date = datetime(2011, 7, 22)
url_base = 'https://json.offtrackbetting.com/tracks/v2/67'
# url = 'https://json.offtrackbetting.com/tracks/v2/82/20110722.json'
toga_obid = '6477d18151290b64e65d327a'
moheegan_obid = '6478055351290b64e65d327e'

for year in range(2011, 2023):
    for month in range(7, 10):
        for day in range(1, 32):
            date_str = f'%d%s%s' % (year, str(month).rjust(2, '0'), str(day).rjust(2, '0'))
            url = f'%s/%s.json' % (url_base, date_str)
            response = requests.get(url)
            document = {
                'track': ObjectId(moheegan_obid),
                'date': date_str,
                'races': []
            }
            if response.ok:
                document['races'] = json.loads(response.content)['events']
                collection.insert_one(document)
            elif response.status_code == 404:
                pass
            else:
                print('unhandled error code: %d' % response.status_code)
                quit()

client.close()