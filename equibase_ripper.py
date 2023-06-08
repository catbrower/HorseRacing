import time
import requests
import selenium
import pytesseract
import undetected_chromedriver as uc

url = 'https://www.equibase.com/premium/eqbPDFChartPlus.cfm?RACE=A&BorP=P&TID=SAR&CTRY=USA&DT=07/14/2022&DAY=D&STYLE=EQB'

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--start-maximized')
with uc.Chrome(options=options) as driver:
    driver.get(url)
    time.sleep(10)
    print()

assert "Python" in driver.title
elem = driver.find_element(By.NAME, "q")
elem.clear()
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
driver.close()