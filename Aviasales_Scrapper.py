from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta
import time
import pandas as pd
import re

# Инициализация драйвера
driver = webdriver.Chrome()

# Чтение маршрутов из CSV файла
routes = pd.read_csv('routes.csv').values
routes_dict = {
    'РЩН': 'TJM',
    'НУР': 'NUX',
    'ДМД': 'DME',
    'УФА': 'UFA',
    'МРВ': 'MRV',
    'СОЧ': 'AER'
}

# Генерация списка маршрутов
directions = [(routes_dict[av], routes_dict[ap]) for av, ap in routes]

# Генерация списка дат
initial_date = datetime.today()
end_date = initial_date + timedelta(days=3)
date_list = [initial_date + timedelta(days=i) for i in range((end_date - initial_date).days + 1)]

# Список с данными по каждому направлению и каждой дате
flights_data = []

for route in directions:
    url = 'https://aviasales.ru/'
    driver.get(url)


    # Ожидание загрузки элементов
    wait = WebDriverWait(driver, 30)
    origin = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="avia_form_origin-input"]')))
    destination = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="avia_form_destination-input"]')))
    date_input = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div[3]/div/form/div[2]/div/button[1]')))

    time.sleep(2)

    # Очистка полей ввода с использованием JavaScript
    driver.execute_script("arguments[0].value = '';", origin)
    origin.send_keys(Keys.CONTROL + "a")
    origin.send_keys(Keys.DELETE)
    time.sleep(1)
    origin.send_keys(route[0])
    time.sleep(1)

    driver.execute_script("arguments[0].value = '';", destination)
    destination.send_keys(Keys.CONTROL + "a")
    destination.send_keys(Keys.DELETE)
    time.sleep(1)
    destination.send_keys(route[1])
    time.sleep(3)

    date_input.click()
    time.sleep(1)

    # Поиск и нажатие нужного элемента всплывающего окна с датами
    date_button = driver.find_element(By.CSS_SELECTOR, 'button[data-test-id="start-date-field"]')
    date_button.click()
    date_element = driver.find_element(By.CSS_SELECTOR, f"div[data-test-id='date-{initial_date.strftime('%d.%m.%Y')}']")
    date_element.click()
    time.sleep(1)

    # Отмена выбора даты обратного рейса
    back_decline = driver.find_element(By.CSS_SELECTOR, 'button[data-test-id="calendar-action-button"]')
    back_decline.click()
    time.sleep(5)

    # Ожидание загрузки элемента
    wait = WebDriverWait(driver, 10)

    # Находим путь к элементу выбора открытия ссылки сайта Островок с отелями
    checkbox = wait.until(EC.presence_of_element_located((By.XPATH, "//label[@data-test-id='checkbox']//input[@type='checkbox']")))

    # Переходим к чекбоксу этого элемента
    actions = ActionChains(driver)
    actions.move_to_element(checkbox).perform()

    # Проверка состояния чекбокса: если галочка стоит, то убираем её
    is_checked = checkbox.is_selected()
    if is_checked:
        driver.execute_script("arguments[0].click();", checkbox)

    search_button = driver.find_element(By.CSS_SELECTOR, 'button[data-test-id="form-submit"]')
    search_button.click()
    time.sleep(15)

    # Переход по датам и сбор данных
    for date in date_list:
        try:
            if date != initial_date:
                formatted_date = date.strftime("%d%m")
                url = driver.current_url
                pattern = r'(\d{2}\d{2})'
                new_url = re.sub(pattern, str(formatted_date), url)
                driver.get(new_url)
                time.sleep(15)

            wait = WebDriverWait(driver, 50)
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-test-id="ticket-preview"]')))
            time.sleep(7)

            flights = driver.find_elements(By.CSS_SELECTOR, 'div[data-test-id="ticket-preview"]')

            prices = list()
            flight_companies = list()
            ports = list()
            times = list()

            for flight in flights:
                try:
                    home = flight.find_element(By.CSS_SELECTOR, 'span.s__OFj5KzLUB5xFu6CCxdOv[data-test-id="text"]').text
                    away = flight.find_element(By.CSS_SELECTOR, 'span.s__6ks0xmARppLGQ9OlkTEA[data-test-id="text"]').text
                    if "Москва" in route and "DME" not in home and "DME" not in away:
                        continue

                    airlines = flight.find_elements(By.CSS_SELECTOR, 'div.s__OxH0KVgAJVg2DNGFFx0s img')
                    names = [elem.get_attribute('alt') for elem in airlines]

                    if 'Ямал' in names:
                        continue

                    for i in names:
                        if i not in flight_companies:
                            flight_companies.append(i)


                    dep, arr = flight.find_elements(By.CSS_SELECTOR, 'span.s__cw9h2Trm1ZaUTQbcz_f8[data-test-id="text"]')
                    departure = dep.text
                    arrival = arr.text
                    price = flight.find_element(By.CSS_SELECTOR, 'div.s__wfLcPf6IF1Ayy7uJmdtH[data-test-id="text"]').text
                    price = int(''.join([i for i in price if i.isdigit()]))

                    ports.extend([home, away])
                    times.append([departure, arrival])
                    prices.append(price)
                except NoSuchElementException:
                    continue

            min_price = min(prices) if prices else 'Нет данных'
            idx = prices.index(min_price) if prices else 'Нет данных'
            min_departure = times[idx][0] if prices else 'Нет данных'
            min_arrival = times[idx][1] if prices else 'Нет данных'

            date_info = {
                'Дата': date.strftime("%d.%m.%Y"),
                'Аэропорт вылета': ports[0] if ports else 'Нет данных',
                'Аэропорт прилёта': ports[1] if ports else 'Нет данных',
                'Время вылета': min_departure,
                'Время прилёта': min_arrival,
                'Авиакомпания(и)': ', '.join(flight_companies) if flight_companies else 'Нет данных',
                'Минимальная цена билета': min_price
            }
            flights_data.append(date_info)
        except (TimeoutException, ValueError):
            print(f'Рейсы на дату {date.strftime("%d.%m.%Y")} не найдены.')

flights_df = pd.DataFrame(flights_data)

airports_dict = {
    'РЩН': 'TJM',
    'НУР': 'NUX',
    'ДМД': 'DME',
    'УФА': 'UFA',
    'МРВ': 'MRV',
    'СОЧ': 'AER'
}

inverted_airports_dict = {v: k for k, v in airports_dict.items()}
flights_df['Аэропорт вылета'] = flights_df['Аэропорт вылета'].map(inverted_airports_dict)
flights_df['Аэропорт прилёта'] = flights_df['Аэропорт прилёта'].map(inverted_airports_dict)
flights_df.to_csv('Aviasales_Flights.csv', index=False, encoding='utf-8')

driver.quit()