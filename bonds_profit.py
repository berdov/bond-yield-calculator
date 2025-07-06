from datetime import datetime, timedelta
from prettytable import PrettyTable
import sys
import os
import requests
from requests.exceptions import RequestException
from calculator import calc


def extract_description_field(data, field_name):
    for row in data['description']['data']:
        if row[0] == field_name:
            return row[2]
    return None


if os.path.exists('test.txt'):
    sys.stdin = open('test.txt', 'r')

original_print = print

def custom_print(*args, **kwargs):
    formatted_args = [
        f"{arg:.2f}" if isinstance(arg, float) else arg for arg in args
    ]
    original_print(*formatted_args, **kwargs)

print = custom_print

price = current_coupon = coupons = velichina_coupona = date1 = None

ticker = input("Введите тикер облигации (или нажмите Enter для ручного ввода): ").strip()

if ticker:
    try:
        # Получаем основные данные
        url = f"https://iss.moex.com/iss/securities/{ticker}.json?iss.meta=off"
        data = requests.get(url, timeout=5).json()

        if not data['description']['data']:
            raise ValueError("Бумага не найдена")

        date1_str = extract_description_field(data, 'MATDATE')
        date1 = datetime.strptime(date1_str, "%Y-%m-%d")

        velichina_coupona = float(extract_description_field(data, 'COUPONVALUE') or 0)
        coupons = float(extract_description_field(data, 'COUPONFREQUENCY') or 0)
        facevalue = float(extract_description_field(data, 'FACEVALUE') or 1000)

        # Получаем цену и НКД
        board = None
        for row in data['boards']['data']:
            if row[data['boards']['columns'].index('market')] == 'bonds':
                board = row[data['boards']['columns'].index('boardid')]
                break
        if not board:
            board = "TQCB"

        url2 = f"https://iss.moex.com/iss/engines/stock/markets/bonds/boards/{board}/securities/{ticker}.json?iss.meta=off&iss.only=marketdata,securities&marketdata.columns=LAST&securities.columns=ACCRUEDINT"
        md = requests.get(url2, timeout=5).json()

        last_price_raw = md['marketdata']['data'][0][0] if md['marketdata']['data'] else None
        accrued_int_raw = md['securities']['data'][0][0] if md['securities']['data'] else None

        last_price_percent = float(last_price_raw) if last_price_raw else 100
        accrued_int = float(accrued_int_raw) if accrued_int_raw else 0.0

        price = last_price_percent * facevalue / 100.0
        current_coupon = accrued_int

        if coupons == 0:
            raise ValueError("Не удалось определить периодичность купонов")

    except (RequestException, ValueError, KeyError, IndexError) as e:
        print(f"Ошибка при получении данных по тикеру: {e}")
        ticker = ""

if not ticker:
    price = float(input("Сколько стоит бумага сейчас: ").replace(",", "."))
    current_coupon = float(input("Накопленный купонный доход: ").replace(",", "."))
    date1 = datetime.strptime(input("Дата погашения (формат: DD.MM.YYYY): "), "%d.%m.%Y")
    coupons = float(input("Число купонов в год: "))
    velichina_coupona = float(input("Величина купона: ").replace(",", "."))

balance = float(input("Какую сумму будем инвестировать: ").replace(",", "."))
nalog = int(input("Введите НДФЛ в процентах: ")) / 100
comission = float(input("Введите комиссию брокера в процентах: ").replace(",", ".")) / 100
type_of_increase = input("Введите способ увеличения цены бумаги (л - линейно, э - экспоненциально): ")

calc(balance, price, date1, datetime.now(), velichina_coupona, coupons, nalog, comission, type_of_increase, current_coupon)
print("всё!")