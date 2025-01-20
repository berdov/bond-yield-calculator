from datetime import datetime
from prettytable import PrettyTable

original_print = print

def custom_print(*args, **kwargs):
    formatted_args = [
        f"{arg:.2f}" if isinstance(arg, float) else arg for arg in args
    ]
    original_print(*formatted_args, **kwargs)

print = custom_print

def create_table():
    table = PrettyTable()
    table.field_names = ["Номер купона", "Текущая цена бумаги", "Остаток на счете", "Оценочная стоимость", "Число бумаг", "Комиссия"]
    table.align = "c"  
    table.float_format = ".2"  
    return table

def print_table(table):
    print("\nРезультаты купонов:")
    print(table)

def no_reinvest(balance, price, date1, date2, velichina_coupona, coupons, nalog, comission):
    result_comission = 0
    table = create_table()
    start_balance = balance
    difference = date1 - date2
    dni = difference.days
    frac = dni / 365
    amount_of_coupons = frac * coupons
    price_increase = (1000 - price) / amount_of_coupons
    amount_of_bonds = int(balance / (current_coupon + price + price*comission))
    balance -= amount_of_bonds * (current_coupon + price + price*comission)
    table.add_row([0, f"{price:.2f}", f"{balance:.2f}", f"{start_balance:.2f}", amount_of_bonds, comission*price*amount_of_bonds])
    result_comission += comission*price*amount_of_bonds
    for i in range(1, int(amount_of_coupons) + 2):
        if i == int(amount_of_coupons) + 1:
            price = 1000
        elif i == 1:
            price = 1000 - price_increase * int(amount_of_coupons)
        else:
            price += price_increase
        balance += (velichina_coupona * amount_of_bonds)
        estimated_value = price * amount_of_bonds + balance
        table.add_row([i, f"{price:.2f}", f"{balance:.2f}", f"{estimated_value:.2f}", amount_of_bonds, 0])
    print_table(table)
    result_of_investment = price * amount_of_bonds + balance
    printer(result_of_investment, start_balance, frac, result_comission)
    

def linear_reinvest(balance, price, date1, date2, velichina_coupona, coupons, nalog, comission):
    result_comission = 0
    table = create_table()
    start_balance = balance
    difference = date1 - date2
    dni = difference.days
    frac = dni / 365
    amount_of_coupons = frac * coupons
    price_increase = (1000 - price) / amount_of_coupons
    amount_of_bonds = int(balance / (current_coupon + price + price*comission))
    balance -= amount_of_bonds * (price + current_coupon + price*comission)
    result_comission += comission * price * amount_of_bonds
    table.add_row([0, f"{price:.2f}", f"{balance:.2f}", f"{start_balance:.2f}", amount_of_bonds, amount_of_bonds*price*comission])
    for i in range(1, int(amount_of_coupons) + 2):
        if i == int(amount_of_coupons) + 1:
            price = 1000
        elif i == 1:
            price = 1000 - price_increase * int(amount_of_coupons)
        else:
            price += price_increase
        balance += (velichina_coupona * amount_of_bonds)
        skolko_dokupim = int(balance / (price + price*comission))
        amount_of_bonds += skolko_dokupim
        balance -= (skolko_dokupim * price * (1+comission))
        estimated_value = price * amount_of_bonds + balance
        table.add_row([i, f"{price:.2f}", f"{balance:.2f}", f"{estimated_value:.2f}", amount_of_bonds, skolko_dokupim*price*comission])
        result_comission+= skolko_dokupim*price*comission
    print_table(table)
    result_of_investment = price * amount_of_bonds + balance
    printer(result_of_investment, start_balance, frac, result_comission)
    
    

def printer(result_of_investment, start_balance, frac, result_comission):
    print("ИТОГИ")
    print("баланс составил", result_of_investment)
    print("доход за все время составит ", (result_of_investment / start_balance - 1) * 100, "%")
    print("процентов годовых", ((result_of_investment / start_balance) ** (1 / frac) - 1) * 100, "%")
    print("комиссия брокера составила", result_comission)
    print("ВЫЧТЕМ ПОДОХОДНЫЙ НАЛОГ")
    after_nalog = result_of_investment - (result_of_investment - start_balance) * nalog
    print("баланс состаит", after_nalog)
    print("доход за все время составит ", ((after_nalog) / start_balance - 1) * 100, "%")
    print("процентов годовых", ((after_nalog / start_balance) ** (1 / frac) - 1) * 100, "%")



print("сколько стоит бумага сейчас")
price = float(input().replace(",", "."))
print("накопленный купонный доход")
current_coupon = float(input().replace(",", "."))
print("дата погашения формат: DD.MM.YYYY")
date1 = datetime.strptime(input(), "%d.%m.%Y")
print("число купонов в год")
coupons = float(input())
print("величина купона")
velichina_coupona = float(input().replace(",", "."))
print("какую сумму будем инвестировать")
balance = float(input().replace(",", "."))
print("введите НДФЛ в процентах")
nalog = int(input()) / 100
date2 = datetime.now()
print("введите комиссию брокера в процентах")
comission = float(input().replace(",", "."))/100
print("купоны реинвестируем? (да/нет/не знаю)")
what = input()
if what == "да":
    linear_reinvest(balance, price, date1, date2, velichina_coupona, coupons, nalog, comission)
elif what == "нет":
    no_reinvest(balance, price, date1, date2, velichina_coupona, coupons, nalog, comission)
elif what == "не знаю":
    no_reinvest(balance, price, date1, date2, velichina_coupona, coupons, nalog, comission)
    print("\n\n")
    linear_reinvest(balance, price, date1, date2, velichina_coupona, coupons, nalog, comission)
print("всё!")