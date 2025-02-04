from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import time
import pandas as pd
import re

# Инициализация драйвера
driver = webdriver.Chrome()

# Чтение маршрутов из CSV файла
routes = pd.read_csv('routes.csv').values
routes_dict = {
    'РЩН': 'Тюмень',
    'НУР': 'Новый Уренгой',
    'ДМД': 'Москва',
    'УФА': 'Уфа',
    'МРВ': 'Минеральные воды',
    'СОЧ': 'Сочи'
}

# Генерация списка маршрутов
directions = list()
for av, ap in routes:
    directions.append([routes_dict[av], routes_dict[ap]])

# Генерация списка дат
initial_date = datetime.today()  # Точка отсчёта
end_date = initial_date + timedelta(days=3)   # Конечная дата (через три дня)

# Список дат, по которому будет проходить парсер
date_list = []
current_date = initial_date
while current_date <= end_date:
    date_list.append(current_date)
    current_date += timedelta(days=1)

# Список с данными по каждому направлению и каждой дате
flights_data = list()

for route in directions:
    url = 'https://avia.tutu.ru/'
    driver.get(url)

    # Ожидание загрузки элементов
    wait = WebDriverWait(driver, 30)
    origin = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[1]/div[1]/div/div[1]/span/div/div/input')))
    destination = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[1]/div[2]/div/div[1]/span/div/div/input')))
    date_input = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[2]/div[1]/div/div/div/input')))
    search_button = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/button/div/div')))

    # Очистка полей ввода с использованием JavaScript
    driver.execute_script("arguments[0].value = '';", origin)
    origin.send_keys(Keys.CONTROL + "a")
    origin.send_keys(Keys.DELETE)
    time.sleep(1)

    driver.execute_script("arguments[0].value = '';", destination)
    destination.send_keys(Keys.CONTROL + "a")
    destination.send_keys(Keys.DELETE)
    time.sleep(1)

    driver.execute_script("arguments[0].value = '';", date_input)
    date_input.send_keys(Keys.CONTROL + "a")
    date_input.send_keys(Keys.DELETE)
    time.sleep(1)

    # Ввод данных
    origin.send_keys(route[0])
    time.sleep(1)
    destination.send_keys(route[1])
    time.sleep(1)
    date_input.send_keys(initial_date.strftime("%d.%m.%Y"))
    time.sleep(1)

    # Нажатие на кнопку поиска
    search_button.click()
    time.sleep(7)

    # Переход по датам и сбор данных
    for date in date_list:
        try:
            # Форматируем дату для URL
            formatted_date = date.strftime("%d%m%Y")  # Формат: ДДММГГГГ
            # Список всех цен на определённую дату
            prices = list()
            flight_companies = list()
            ports = list()

            # Формируем URL для текущей даты, заменяя 8-значную подстроку из цифр актуальной датой
            url = driver.current_url
            pattern = r'(\d{2}\d{2}\d{4})'
            new_url = re.sub(pattern, str(formatted_date), url)
            driver.get(new_url)
            time.sleep(7)

            # Ожидание появления всех рейсов
            wait = WebDriverWait(driver, 30)
            flights = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_3fTfvjX4bphQxDYxgAddwX')))

            # Прокручиваем страницу вниз, иначе парсер рискует не увидеть все видимые веб-элементы рейсов на странице
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(7)  # Ожидание загрузки новых элементов

            # Повторный поиск элементов
            flights = driver.find_elements(By.CLASS_NAME, '_3fTfvjX4bphQxDYxgAddwX')

            # Сбор данных для каждого рейса
            for flight in flights:
                wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'span._12UBdZovHdMWXrLfBbH8zS[data-ti="place"]')))
                airports = flight.find_elements(By.CSS_SELECTOR, 'span._12UBdZovHdMWXrLfBbH8zS[data-ti="place"]')
                home = False
                away = False
                if airports:
                    home = airports[0].text
                    away = airports[1].text
                else:
                    home = 'Не найдено'
                    away = 'Не найдено'

                if "Москва" in route and "Домодедово" not in home and "Домодедово" not in away:
                    continue
                ports.append(home)
                ports.append(away)
                airlines = [elem.text for elem in flight.find_elements(By.CSS_SELECTOR, '._19j5UevMdTcHGRMJLu4Wtd.o-text-inline.o-text-paragraphSmall')]
                if 'Ямал' in airlines:
                    if len(airlines) > 1:
                        continue

                for airline in airlines:
                    if airline not in flight_companies:
                        flight_companies.append(airline)

                price = flight.find_element(By.CSS_SELECTOR, '._2Q5MrZ0v-FU4A28a-_xBFr.o-price-nowrap.o-text-inline.o-text-headerMedium.o-text-headerLarge-md').text
                price = ''.join([i for i in price if i.isdigit()])
                prices.append(price)

            # Создаем словарь с информацией о направлении на определённую дату
            date_info = {
                'Дата': date.strftime("%d.%m.%Y"),
                'Аэропорт вылета': ports[0] if len(ports) > 0 else 'Нет данных',
                'Аэропорт прилёта': ports[1] if len(ports) > 0 else 'Нет данных',
                'Авиакомпания(и)': ', '.join(flight_companies) if len(flight_companies) > 0 else 'Нет данных',
                'Минимальная цена билета': min(prices) if len(prices) > 0 else 'Нет данных'
            }
            flights_data.append(date_info)
        except TimeoutException:
            print(f'Рейсы на дату {date.strftime("%d.%m.%Y")} не найдены.')

# Сохранение данных в CSV файл
flights_df = pd.DataFrame(flights_data)
flights_df.to_csv('TuTu_Flights.csv', index=False, encoding='utf-8')

# Закрытие драйвера
driver.quit()
