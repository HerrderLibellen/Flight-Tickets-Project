from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
url = 'https://avia.tutu.ru/'

driver.get(url)
time.sleep(3)

# Парсинг информации по направлению Тюмень - Новый Уренгой
origin = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[1]/div[1]/div/div[1]/span/div/div/input')
origin.click()
origin.send_keys('Тюмень')
time.sleep(1)

destination = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[1]/div[2]/div/div[1]/span/div/div/input')
destination.click()
destination.send_keys('Новый Уренгой')
time.sleep(1)

# Точка отсчёта
initial_date = '31.01.2025'

date = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[2]/div[1]/div/div/div/input')
date.click()
date.send_keys(initial_date)
time.sleep(1)

search = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/button/div/div')
search.click()
time.sleep(10)

# Поиск элементов
airlines = driver.find_elements(By.CSS_SELECTOR, '._19j5UevMdTcHGRMJLu4Wtd.o-text-inline.o-text-paragraphSmall')
departures = driver.find_elements(By.CSS_SELECTOR, '.UFlg3tcFvqtPw3IuhhhM3.o-text-inline.o-text-headerMedium.o-text-headerLarge-md')
arrivals = driver.find_elements(By.CSS_SELECTOR, '._15mC1UzJwjHpnQolp1FCYX.o-text-inline.o-text-headerMedium.o-text-headerLarge-md')
prices = driver.find_elements(By.CSS_SELECTOR, '._2Q5MrZ0v-FU4A28a-_xBFr.o-price-nowrap.o-text-inline.o-text-headerMedium.o-text-headerLarge-md')

# Словарь с информацией о рейсах по датам
flights_by_date = {}
min_prices_by_date = {}
flights = []

# Функция для очистки ценовых данных от символов, неадекватно отображающихся в консоли
# (тонкие пробелы, символы рубля и символы нулевой ширины)
def clean_price(price):
    cleaned_price = price.replace('\u2009', '').replace('\u2060', '')
    cleaned_price = cleaned_price.replace('\u20BD', '')
    return cleaned_price

for i in range(len(airlines)):
    flight_info = {}
    flight_info['Авиакомпания'] = airlines[i].text
    flight_info['Время отправления'] = departures[i].text
    flight_info['Время прибытия'] = arrivals[i].text
    flight_info['Цена'] = clean_price(prices[i].text)
    flights.append(flight_info)

driver.quit()
flights_by_date[initial_date] = flights
print(flights_by_date)





