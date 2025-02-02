from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime, timedelta
import time
import json
import pandas as pd

driver = webdriver.Chrome()

# Генерация списка дат
initial_date = datetime.today()  # Точка отсчёта
end_date = initial_date + timedelta(days=90)   # Конечная дата (через три месяца)

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
    try:
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
            airlines = ', '.join([elem.text for elem in flight.find_elements(By.CSS_SELECTOR, '._19j5UevMdTcHGRMJLu4Wtd.o-text-inline.o-text-paragraphSmall')])
            departure = flight.find_element(By.CSS_SELECTOR, '.UFlg3tcFvqtPw3IuhhhM3.o-text-inline.o-text-headerMedium.o-text-headerLarge-md').text
            arrival = flight.find_element(By.CSS_SELECTOR, '._15mC1UzJwjHpnQolp1FCYX.o-text-inline.o-text-headerMedium.o-text-headerLarge-md').text
            price = flight.find_element(By.CSS_SELECTOR, '._2Q5MrZ0v-FU4A28a-_xBFr.o-price-nowrap.o-text-inline.o-text-headerMedium.o-text-headerLarge-md').text
            price = ''.join([i for i in price if i.isdigit()])
            prices.append(price)

            # Создаем словарь с информацией о рейсе
            flight_info = {
                        'Дата': date.strftime("%d.%m.%Y"),
                        'Авиакомпания(и)': airlines,
                        'Время отправления': departure,
                        'Время прибытия': arrival,
                        'Цена билета': price
                    }
            # Добавляем словарь в список
            flights_data.append(flight_info)
        # В другой словарь добавляем минимальную стоимость билета за определённую дату
        min_prices_by_date[date.strftime("%d.%m.%Y")] = min(prices)
    except TimeoutException:
        print(f'Рейсы на дату {date.strftime("%d.%m.%Y")} не найдены.')

flights_df = pd.DataFrame(flights_data)
flights_df.to_csv('Tyumen-Novy_Urengoy_flights.csv', index=False, encoding='utf-8')
min_prices_df = [{'Дата': date, 'Минимальная цена': price} for date, price in min_prices_by_date.items()]
min_prices_df = pd.DataFrame(min_prices_df)
min_prices_df.to_csv('min_prices_Tyumen-Novy_Urengoy', index=False, encoding='utf-8')
driver.quit()