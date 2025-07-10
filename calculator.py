from datetime import datetime, timedelta
from prettytable import PrettyTable
import pandas as pd


# Красивый print для чисел
original_print = print
def custom_print(*args, **kwargs):
    formatted_args = [
        f"{arg:.2f}" if isinstance(arg, float) else arg
        for arg in args
    ]
    original_print(*formatted_args, **kwargs)

print = custom_print


def create_table():
    table = PrettyTable()
    table.field_names = ["Номер купона", "Дата выплаты", "КД", "Текущая цена", "Остаток на счете",
                         "Оценочная стоимость", "Всего бумаг", "Докупили", "Комиссия", "Налог"]
    table.align = "c"
    table.float_format = ".2"
    return table


def generate_price_schedule(start_price, coupon_dates, increase_type):
    """Генерация графика роста цены бумаги к дате погашения"""
    prices = []
    total_steps = len(coupon_dates)
    final_price = 1000.0

    if total_steps == 1:
        return [final_price]

    if increase_type == 'л':
        for i in range(total_steps):
            step_price = start_price + (final_price - start_price) * i / (total_steps - 1)
            prices.append(step_price)
    else:
        factor = (final_price / start_price) ** (1 / (total_steps - 1))
        current = start_price
        for _ in range(total_steps):
            prices.append(current)
            current *= factor

    return prices


def calc(balance, start_price, maturity_date, today, coupon_value, coupons_per_year,
         tax_rate, commission_rate, increase_type, current_accrued_coupon,
         coupon_dates, type_of_account, output):

    total_commission_paid = 0
    initial_balance = balance
    number_of_bonds = int(balance / (start_price + current_accrued_coupon + start_price * commission_rate))
    balance -= number_of_bonds * (start_price + current_accrued_coupon + start_price * commission_rate)

    table = create_table()
    data = []

    table.add_row([
        0,
        today.strftime("%d %m %Y"),
        0,
        f"{start_price:.2f}",
        f"{balance:.2f}",
        f"{initial_balance:.2f}",
        0,
        number_of_bonds,
        start_price * number_of_bonds * commission_rate,
        0
    ])

    data.append({
        "Номер купона": 0,
        "Дата выплаты": today.strftime("%d %m %Y"),
        "КД": 0,
        "Текущая цена": start_price,
        "Остаток на счете": balance,
        "Оценочная стоимость": initial_balance,
        "Всего бумаг": 0,
        "Докупили": number_of_bonds,
        "Комиссия": start_price * number_of_bonds * commission_rate,
        "Налог": 0
    })

    total_commission_paid += start_price * number_of_bonds * commission_rate
    price_schedule = generate_price_schedule(start_price, coupon_dates, increase_type)

    for i, (coupon_date, bond_price) in enumerate(zip(coupon_dates, price_schedule), start=1):
        balance += coupon_value * number_of_bonds
        additional_bonds = int(balance / (bond_price * (1 + commission_rate)))
        number_of_bonds += additional_bonds
        balance -= additional_bonds * bond_price * (1 + commission_rate)

        estimated_value = bond_price * number_of_bonds + balance
        commission_paid = additional_bonds * bond_price * commission_rate
        tax_paid = coupon_value * number_of_bonds * tax_rate
        total_commission_paid += commission_paid

        row = {
            "Номер купона": i,
            "Дата выплаты": coupon_date.strftime("%d %m %Y"),
            "КД": coupon_value * number_of_bonds,
            "Текущая цена": bond_price,
            "Остаток на счете": balance,
            "Оценочная стоимость": estimated_value,
            "Всего бумаг": number_of_bonds,
            "Докупили": additional_bonds,
            "Комиссия": commission_paid,
            "Налог": tax_paid
        }

        data.append(row)
        table.add_row([
            i,
            row["Дата выплаты"],
            row["КД"],
            row["Текущая цена"],
            row["Остаток на счете"],
            row["Оценочная стоимость"],
            row["Всего бумаг"],
            row["Докупили"],
            row["Комиссия"],
            row["Налог"]
        ])

    final_value = bond_price * number_of_bonds + balance
    total_years = (maturity_date - today).days / 365.0
    annual_return = ((final_value / initial_balance) ** (1 / total_years) - 1) * 100
    after_tax = final_value - (final_value - initial_balance) * tax_rate
    after_tax_annual = ((after_tax / initial_balance) ** (1 / total_years) - 1) * 100

    # Итоги (включаются в файл)
    summary_rows = [
        {"Номер купона": "ИТОГИ", "Дата выплаты": "", "КД": "", "Текущая цена": "", "Остаток на счете": "", "Оценочная стоимость": final_value, "Всего бумаг": "", "Докупили": "", "Комиссия": total_commission_paid, "Налог": ""},
        {"Номер купона": "Доход за всё время", "Оценочная стоимость": (final_value / initial_balance - 1) * 100},
        {"Номер купона": "Процентов годовых", "Оценочная стоимость": annual_return},
        {"Номер купона": "После вычета НДФЛ", "Оценочная стоимость": after_tax},
        {"Номер купона": "Доход после НДФЛ", "Оценочная стоимость": ((after_tax / initial_balance - 1) * 100)},
        {"Номер купона": "Годовых после НДФЛ", "Оценочная стоимость": after_tax_annual}
    ]

    data.extend(summary_rows)

    # Вывод
    if output.lower() == "t" or output.lower() == "т":
        print("\nРезультаты купонов:")
        print(table)
        for row in summary_rows:
            print(row["Номер купона"], row.get("Оценочная стоимость", ""))
    elif output.lower() == "c" or output.lower() == "с":
        df = pd.DataFrame(data)
        df.to_csv("results.csv", index=False)
        print("Данные сохранены в results.csv")
    elif output.lower() == "e" or output.lower() == "е":
        df = pd.DataFrame(data)
        df.to_excel("results.xlsx", index=False)
        print("Данные сохранены в results.xlsx")