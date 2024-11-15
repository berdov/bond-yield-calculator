from datetime import datetime
from prettytable import PrettyTable

# Сохраняем оригинальную функцию print
original_print = print

# Переопределяем print для форматирования чисел типа float
def custom_print(*args, **kwargs):
    formatted_args = [
        f"{arg:.2f}" if isinstance(arg, float) else arg for arg in args
    ]
    original_print(*formatted_args, **kwargs)

# Подменяем стандартную функцию print на custom_print
print = custom_print

def calculate_bond_investment(balance, price, date1, date2, coupon_value, coupons, tax_rate, reinvest):
    start_balance = balance
    days = (date1 - date2).days
    frac = days / 365
    num_coupons = int(frac * coupons)
    price_increment = (1000 - price) / num_coupons

    bonds = int(balance / (price + current_coupon))
    balance -= bonds * (price + current_coupon)

    # Таблица для отображения результатов
    table = PrettyTable()
    table.field_names = ["Купон №", "Цена бумаги", "Остаток баланса", "Количество бумаг", "Оценочная стоимость"]

    for i in range(1, num_coupons + 2):
        if i == num_coupons + 1:
            price = 1000
        elif i > 1:
            price += price_increment

        balance += coupon_value * bonds

        if reinvest:
            additional_bonds = int(balance / price)
            bonds += additional_bonds
            balance -= additional_bonds * price

        table.add_row([i, price, balance, bonds, bonds * price + balance])

    final_value = bonds * price + balance
    profit = (final_value / start_balance - 1) * 100
    annualized_return = ((final_value / start_balance) ** (1 / frac) - 1) * 100

    # Вывод таблицы
    print(table)

    # Итоги
    print("ИТОГИ:")
    print("Баланс составил:", final_value)
    print("Доход за всё время:", profit, "%")
    print("Процентов годовых:", annualized_return, "%")

    # Учёт налога
    after_tax = final_value - (final_value - start_balance) * tax_rate
    tax_profit = (after_tax / start_balance - 1) * 100
    tax_annualized_return = ((after_tax / start_balance) ** (1 / frac) - 1) * 100

    print("После вычета налога:")
    print("Баланс составил:", after_tax)
    print("Доход за всё время:", tax_profit, "%")
    print("Процентов годовых:", tax_annualized_return, "%")


# Ввод данных
print("Сколько стоит бумага сейчас:")
price = float(input())
print("Накопленный купонный доход:")
current_coupon = float(input())
print("Дата погашения (формат: DD.MM.YYYY):")
date1 = datetime.strptime(input(), "%d.%m.%Y")
print("Число купонов в год:")
coupons = float(input())
print("Величина купона:")
coupon_value = float(input())
print("Какую сумму будем инвестировать:")
balance = float(input())
print("Введите НДФЛ в процентах:")
tax_rate = float(input()) / 100
date2 = datetime.now()
print("Купоны реинвестируем? (да/нет/не знаю):")
reinvest_choice = input()

# Обработка выбора
if reinvest_choice == "да":
    print("Случай 2. Купоны реинвестируются.")
    calculate_bond_investment(balance, price, date1, date2, coupon_value, coupons, tax_rate, reinvest=True)
elif reinvest_choice == "нет":
    print("Случай 1. Купоны не реинвестируются.")
    calculate_bond_investment(balance, price, date1, date2, coupon_value, coupons, tax_rate, reinvest=False)
elif reinvest_choice == "не знаю":
    print("Случай 1. Купоны не реинвестируются.")
    calculate_bond_investment(balance, price, date1, date2, coupon_value, coupons, tax_rate, reinvest=False)
    print("\nСлучай 2. Купоны реинвестируются.")
    calculate_bond_investment(balance, price, date1, date2, coupon_value, coupons, tax_rate, reinvest=True)

print("Всё!")