from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
import time
import json
import pandas as pd

# Функция для преобразования записи даты в коде страницы сайта в формат datetime
def format_date(date_str, year=2025):
    months = {
        'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4,
        'май': 5, 'июн': 6, 'июл': 7, 'авг': 8,
        'сен': 9, 'окт': 10, 'ноя': 11, 'дек': 12
    }
    day, month, wd = date_str.split()
    month = months.get(month, 1)
    date_obj = datetime(year=year, month=month, day=int(day))
    return date_obj.strftime("%d.%m.%Y")

driver = webdriver.Chrome()

# Генерация списка дат
initial_date = datetime(2025, 2, 1)  # Точка отсчёта
end_date = datetime(2025, 5, 1)   # Конечная дата (через три месяца)
# Список дат, по которому будет проходить парсер
date_list = []
current_date = initial_date
while current_date <= end_date:
    date_list.append(current_date)
    current_date += timedelta(days=1)

# Список для хранения данных о рейсах
flights_data = []
# Список для хранения дат и минимальной представленной цены на каждую из них
min_prices_by_date = dict()

# Переход по датам и сбор данных
for date in date_list:
    # Форматируем дату для URL
    formatted_date = date.strftime("%d%m%Y")  # Формат: ДДММГГГГ
    # Список всех цен на определённую дату
    prices = []

    # Формируем URL для текущей даты
    url = f'https://avia.tutu.ru/f/Tyumen/Noviy_urengoy/?class=Y&passengers=100&route[0]=86-{formatted_date}-59&travelers=1'
    driver.get(url)

    # Ожидание появления всех рейсов
    wait = WebDriverWait(driver, 10)
    flights = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_3fTfvjX4bphQxDYxgAddwX')))

    # Прокручиваем страницу вниз, иначе парсер рискует не увидеть все видимые веб-элементы рейсов на странице
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(7)  # Ожидание загрузки новых элементов

    # Повторный поиск элементов
    flights = driver.find_elements(By.CLASS_NAME, '_3fTfvjX4bphQxDYxgAddwX')

    # Сбор данных для каждого рейса
    for flight in flights:
        date_str = flight.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div[3]/div[1]/div/div/div[1]/div[2]/div/div[3]/div[1]/span[1]').text
        date_formatted = format_date(date_str)
        airlines = [elem.text for elem in flight.find_elements(By.CSS_SELECTOR, '._19j5UevMdTcHGRMJLu4Wtd.o-text-inline.o-text-paragraphSmall')]
        departure = flight.find_element(By.CSS_SELECTOR, '.UFlg3tcFvqtPw3IuhhhM3.o-text-inline.o-text-headerMedium.o-text-headerLarge-md').text
        arrival = flight.find_element(By.CSS_SELECTOR, '._15mC1UzJwjHpnQolp1FCYX.o-text-inline.o-text-headerMedium.o-text-headerLarge-md').text
        price = flight.find_element(By.CSS_SELECTOR, '._2Q5MrZ0v-FU4A28a-_xBFr.o-price-nowrap.o-text-inline.o-text-headerMedium.o-text-headerLarge-md').text
        price = ''.join([i for i in price if i.isdigit()])
        prices.append(price)

        # Создаем словарь с информацией о рейсе
        flight_info = {
                        'Дата': date_formatted,
                        'Авиакомпания(и)': airlines,
                        'Время отправления': departure,
                        'Время прибытия': arrival,
                        'Цена билета': price
                    }

        # Добавляем словарь в список
        flights_data.append(flight_info)
    # В другой словарь добавляем минимальную стоимость билета за определённую дату
    min_prices_by_date[date.strftime("%d.%m.%Y")] = min(prices)

print(flights_data[:5])
print('Минимальные цены на авиабилеты по датам:')
print(min_prices_by_date)
driver.quit()