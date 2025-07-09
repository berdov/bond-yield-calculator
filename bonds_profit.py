from datetime import datetime
import sys
import os
import requests
from requests.exceptions import RequestException
from datetime import timedelta, datetime


from calculator import calc, generate_price_schedule

def extract_field(description_data, field_name):
    for row in description_data['description']['data']:
        if row[0] == field_name:
            return row[2]
    return None

def fetch_bond_data_from_moex(ticker):
    try:
        url = f"https://iss.moex.com/iss/securities/{ticker}.json?iss.meta=off"
        description_data = requests.get(url, timeout=5).json()

        if not description_data['description']['data']:
            raise ValueError("Бумага не найдена на MOEX")

        maturity_str = extract_field(description_data, 'MATDATE')
        coupon_value_str = extract_field(description_data, 'COUPONVALUE')
        coupon_freq_str = extract_field(description_data, 'COUPONFREQUENCY')
        face_value_str = extract_field(description_data, 'FACEVALUE')

        maturity_date = datetime.strptime(maturity_str, "%Y-%m-%d") if maturity_str else None
        coupon_value = float(coupon_value_str or 0)
        coupon_frequency = int(float(coupon_freq_str or 0))
        face_value = float(face_value_str or 1000)

        board = None
        for row in description_data['boards']['data']:
            market_idx = description_data['boards']['columns'].index('market')
            boardid_idx = description_data['boards']['columns'].index('boardid')
            if row[market_idx] == 'bonds':
                board = row[boardid_idx]
                break
        if not board:
            board = 'TQCB'

        url2 = (
            f"https://iss.moex.com/iss/engines/stock/markets/bonds/boards/{board}/"
            f"securities/{ticker}.json?iss.meta=off&iss.only=marketdata,securities"
            f"&marketdata.columns=LAST&securities.columns=ACCRUEDINT"
        )
        md = requests.get(url2, timeout=5).json()

        last_price_raw = md['marketdata']['data'][0][0] if md['marketdata']['data'] else None
        if last_price_raw is None:
            price_percent = float(input("Введите цену бумаги в процентах от номинала: ").replace(",", "."))
        else:
            price_percent = float(last_price_raw)

        price = price_percent * face_value / 100
        accrued_coupon = float(md['securities']['data'][0][0]) if md['securities']['data'] else 0.0

        if coupon_frequency == 0:
            raise ValueError("Не удалось определить периодичность купонов")

        return {
            "price": price,
            "accrued_coupon": accrued_coupon,
            "maturity_date": maturity_date,
            "coupon_frequency": coupon_frequency,
            "coupon_value": coupon_value,
        }

    except (RequestException, ValueError, KeyError, IndexError) as e:
        print(f"Ошибка при получении данных по тикеру: {e}")
        return None

def prompt_manual_bond_data():
    price = float(input("Сколько стоит бумага сейчас: ").replace(",", "."))
    accrued_coupon = float(input("Накопленный купонный доход: ").replace(",", "."))
    maturity_date = datetime.strptime(input("Дата погашения (ДД.ММ.ГГГГ): "), "%d.%m.%Y")
    coupon_frequency = int(input("Число купонов в год: "))
    coupon_value = float(input("Величина купона: ").replace(",", "."))
    return {
        "price": price,
        "accrued_coupon": accrued_coupon,
        "maturity_date": maturity_date,
        "coupon_frequency": coupon_frequency,
        "coupon_value": coupon_value
    }

def get_user_investment_parameters():
    total_investment = float(input("Сколько инвестируем: ").replace(",", "."))
    tax_rate = float(input("Введите НДФЛ (%): ").replace(",", ".")) / 100
    commission_rate = float(input("Комиссия брокера (%): ").replace(",", ".")) / 100
    increase_type = input("Тип роста цены (л - линейный, э - экспоненциальный): ").strip().lower()
    return total_investment, tax_rate, commission_rate, increase_type

def get_known_coupon_dates_from_moex(ticker):
    try:
        url = f"https://iss.moex.com/iss/securities/{ticker}/bondization.json"
        response = requests.get(url, timeout=5)
        data = response.json()
        rows = data.get("coupons", {}).get("data", [])
        columns = data.get("coupons", {}).get("columns", [])
        date_idx = columns.index("coupondate")
        dates = [datetime.strptime(row[date_idx], "%Y-%m-%d") for row in rows if row[date_idx]]
        return sorted(set(dates))
    except Exception as e:
        print(f"Ошибка при получении дат купонов: {e}")
        return []


def build_coupon_schedule(maturity_date, coupon_frequency, known_coupon_dates, today):
    """
    Строит расписание дат выплаты купонов:
    - если известны даты в будущем — использует их
    - если известны только прошедшие даты — достраивает
    - если дат вообще нет — строит равномерно между today и maturity_date
    """
    # Оставляем только будущие купоны
    result = [d for d in known_coupon_dates if d >= today]

    # Если нет будущих — строим от maturity_date назад
    if not result:
        delta_days = int(365 / coupon_frequency)
        current = maturity_date
        while current > today:
            result.append(current)
            current -= timedelta(days=delta_days)
        result = sorted(result)

    else:
        # Дополняем равномерно между последней известной датой и maturity_date
        last_known = result[-1]
        remaining_days = (maturity_date - last_known).days
        steps_needed = round(remaining_days / (365 / coupon_frequency))

        if steps_needed > 0:
            for i in range(1, steps_needed + 1):
                next_date = last_known + timedelta(days=i * remaining_days / steps_needed)
                result.append(next_date)

    # Гарантируем наличие финальной даты (точное совпадение)
    if abs((result[-1].date() - maturity_date.date()).days) > 1:
        result.append(maturity_date)

    return sorted(result)

def main():
    if os.path.exists('test_with_ticker.txt'):
        sys.stdin = open('test_with_ticker.txt')

    ticker = input("Введите тикер облигации (или Enter для ручного ввода): ").strip()
    bond_data = fetch_bond_data_from_moex(ticker) if ticker else None
    if not bond_data:
        bond_data = prompt_manual_bond_data()

    total_investment, tax_rate, commission_rate, increase_type = get_user_investment_parameters()
    today = datetime.now()

    known_coupon_dates = get_known_coupon_dates_from_moex(ticker) if ticker else []
    all_coupon_dates = build_coupon_schedule(
        maturity_date=bond_data["maturity_date"],
        coupon_frequency=bond_data["coupon_frequency"],
        known_coupon_dates=known_coupon_dates,
        today=today
    )

    calc(
        balance=total_investment,
        start_price=bond_data["price"],
        maturity_date=bond_data["maturity_date"],
        today=today,
        coupon_value=bond_data["coupon_value"],
        coupons_per_year=bond_data["coupon_frequency"],
        tax_rate=tax_rate,
        commission_rate=commission_rate,
        increase_type=increase_type,
        current_accrued_coupon=bond_data["accrued_coupon"],
        coupon_dates=all_coupon_dates
    )

    print("Готово.")

if __name__ == "__main__":
    main()