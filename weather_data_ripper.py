import json
import requests
from pymongo import MongoClient
from datetime import datetime, timedelta

# url = 'https://api.weather.com/v1/location/KALB:9:US/observations/historical.json?apiKey=e1f10a1e78da46f5b10a1e78da96f525&units=e&startDate=20110601&endDate=20110631'

# response = requests.get(url)

for i in range(12):
    date = datetime(2011, i + 1, 1)
    date_end = date - timedelta(days=1)
    print(date_end)

print()

