from datetime import datetime, timedelta
from prettytable import PrettyTable


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
    table.field_names = ["Номер купона", "Дата выплаты", "Текущая цена бумаги", "Остаток на счете", "Оценочная стоимость", "Число бумаг", "Комиссия"]
    table.align = "c"
    table.float_format = ".2"
    return table

def print_table(table):
    print("\nРезультаты купонов:")
    print(table)


def generate_price_schedule(start_price, coupon_dates, increase_type):
    """Генерация графика роста цены бумаги к дате погашения"""
    prices = []
    total_steps = len(coupon_dates)
    final_price = 1000.0

    if total_steps == 1:
        return [final_price]

    if increase_type == 'л':  # линейный рост
        for i in range(total_steps):
            step_price = start_price + (final_price - start_price) * i / (total_steps - 1)
            prices.append(step_price)
    else:  # экспоненциальный рост
        factor = (final_price / start_price) ** (1 / (total_steps - 1))
        current = start_price
        for _ in range(total_steps):
            prices.append(current)
            current *= factor

    return prices


def calc(balance, start_price, maturity_date, today, coupon_value, coupons_per_year, tax_rate, commission_rate, increase_type, current_accrued_coupon, coupon_dates):
    total_commission_paid = 0
    initial_balance = balance

    number_of_bonds = int(balance / (start_price + current_accrued_coupon + start_price * commission_rate))
    balance -= number_of_bonds * (start_price + current_accrued_coupon + start_price * commission_rate)

    table = create_table()
    table.add_row([
        0,
        today.strftime("%d %m %Y"),
        f"{start_price:.2f}",
        f"{balance:.2f}",
        f"{initial_balance:.2f}",
        number_of_bonds,
        start_price * number_of_bonds * commission_rate
    ])
    total_commission_paid += start_price * number_of_bonds * commission_rate

    price_schedule = generate_price_schedule(start_price, coupon_dates, increase_type)

    for i, (coupon_date, bond_price) in enumerate(zip(coupon_dates, price_schedule), start=1):
        balance += coupon_value * number_of_bonds

        # Покупаем новые бумаги, если хватает средств
        additional_bonds = int(balance / (bond_price * (1 + commission_rate)))
        number_of_bonds += additional_bonds
        balance -= additional_bonds * bond_price * (1 + commission_rate)

        estimated_value = bond_price * number_of_bonds + balance
        commission_paid = additional_bonds * bond_price * commission_rate
        total_commission_paid += commission_paid

        table.add_row([
            i,
            coupon_date.strftime("%d %m %Y"),
            f"{bond_price:.2f}",
            f"{balance:.2f}",
            f"{estimated_value:.2f}",
            number_of_bonds,
            commission_paid
        ])

    print_table(table)

    final_value = bond_price * number_of_bonds + balance
    print("ИТОГИ")
    print("баланс составил", final_value)
    print("доход за всё время составит", (final_value / initial_balance - 1) * 100, "%")

    total_years = (maturity_date - today).days / 365.0
    annual_return = ((final_value / initial_balance) ** (1 / total_years) - 1) * 100
    print("процентов годовых", annual_return, "%")
    print("комиссия брокера составила", total_commission_paid)

    print("ВЫЧТЕМ ПОДОХОДНЫЙ НАЛОГ")
    after_tax = final_value - (final_value - initial_balance) * tax_rate
    print("баланс составит", after_tax)
    print("доход за всё время составит", ((after_tax / initial_balance - 1) * 100), "%")
    print("процентов годовых", ((after_tax / initial_balance) ** (1 / total_years) - 1) * 100, "%")