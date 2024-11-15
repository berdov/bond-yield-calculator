from datetime import datetime

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

def no_reinvest(balance, price, date1, date2, velichina_coupona, coupons, nalog):
    start_balance = balance
    difference = date1 - date2
    dni = difference.days
    frac = dni / 365
    amount_of_coupons = frac * coupons
    price_increase = (1000 - price) / amount_of_coupons
    amount_of_bonds = int(balance / (current_coupon + price))
    print("бумаг куплено", amount_of_bonds)
    balance -= amount_of_bonds * (price + current_coupon)
    print("текущий остаток кошелька", format(balance, '.2f'))
    for i in range(1, int(amount_of_coupons) + 2):
        print("номер купона", i)
        if i == int(amount_of_coupons) + 1:
            price = 1000
        elif i == 1:
            price = 1000 - price_increase * int(amount_of_coupons)
        else:
            price += price_increase
        balance += (velichina_coupona * amount_of_bonds)
        skolko_dokupim = int(balance / price)
        print("текущая примерная стоимость бумаги", price)
        print("текущий остаток кошелька", format(balance, '.2f'))
        print("текущая оценочная стоимость", price * amount_of_bonds + balance)
    result_of_investment = price * amount_of_bonds + balance
    print("ИТОГИ")
    print("баланс составил", result_of_investment)
    print("доход за все время составит ", (result_of_investment / start_balance - 1) * 100, "%")
    print("процентов годовых", ((result_of_investment / start_balance) ** (1 / frac) - 1) * 100, "%")
    print("ВЫЧТЕМ ПОДОХОДНЫЙ НАЛОГ")
    after_nalog = result_of_investment - (result_of_investment - start_balance) * nalog
    print("баланс состаит", after_nalog)
    print("доход за все время составит ", ((after_nalog) / start_balance - 1) * 100, "%")
    print("процентов годовых", ((after_nalog / start_balance) ** (1 / frac) - 1) * 100, "%")

def linear_reinvest(balance, price, date1, date2, velichina_coupona, coupons, nalog):
    start_balance = balance
    difference = date1 - date2
    dni = difference.days
    frac = dni / 365
    amount_of_coupons = frac * coupons
    price_increase = (1000 - price)/amount_of_coupons
    amount_of_bonds = int(balance/(current_coupon+price))
    print("бумаг куплено", amount_of_bonds)
    balance -= amount_of_bonds*(price+current_coupon)
    print("текущий остаток кошелька", balance)
    for i in range(1, int(amount_of_coupons)+2):
        print("номер купона", i)
        if i == int(amount_of_coupons)+1:
            price = 1000
        elif i == 1:
            price = 1000 - price_increase*int(amount_of_coupons)
        else:
            price += price_increase
        balance += (velichina_coupona*amount_of_bonds)
        skolko_dokupim = int(balance/price)
        amount_of_bonds += skolko_dokupim
        balance -= (skolko_dokupim*price)
        print("сколько стало бумаг", amount_of_bonds)
        print("текущая примерная стоимость бумаги", price)
        print("текущий остаток кошелька", balance)
        print("текущая оценочная стоимость", price*amount_of_bonds + balance)
    result_of_investment = price*amount_of_bonds + balance
    print("ИТОГИ")
    print("баланс составил", result_of_investment)
    print("доход за все время составит ", (result_of_investment / start_balance - 1) * 100, "%")
    print("процентов годовых", ((result_of_investment / start_balance) ** (1 / frac) - 1) * 100, "%")
    print("ВЫЧТЕМ ПОДОХОДНЫЙ НАЛОГ")
    after_nalog = result_of_investment - (result_of_investment - start_balance)*nalog
    print("баланс состаит", after_nalog)
    print("доход за все время составит ", ((after_nalog) / start_balance - 1) * 100, "%")
    print("процентов годовых", ((after_nalog / start_balance) ** (1 / frac) - 1) * 100, "%")



#print(format(a, '.2f'))
#самописка чтобы считать доходность облигации в процентах годовых при условии что купоны не реинвестируются
print("сколько стоит бумага сейчас")
price = float(input())
print("накопленный купонный доход")
current_coupon = float(input())
print("дата погашения формат: DD.MM.YYYY")
date1 = datetime.strptime(input(), "%d.%m.%Y")
print("число купонов в год")
coupons = (float(input()))
print("величина купона")
velichina_coupona = float(input())
print("какую сумму будем инвестировать")
balance = float(input())
print("введите НДФЛ в процентах")
nalog = int(input())
nalog = nalog / 100
date2 = datetime.now()
print("купоны реинвестируем? (да/нет/не знаю)")
what = input()
if what == "да":
    print("случай 2. Купоны реинвестируются)")
    linear_reinvest(balance, price, date1, date2, velichina_coupona, coupons, nalog)
elif what == "нет":
    print("случай 1. Купоны не реинвестируются")
    no_reinvest(balance, price, date1, date2, velichina_coupona, coupons, nalog)
elif what == "не знаю":
    print("случай 1. Купоны не реинвестируются")
    no_reinvest(balance, price, date1, date2, velichina_coupona, coupons, nalog)
    print("")
    print("")
    print("случай 2. Купоны реинвестируются")
    linear_reinvest(balance, price, date1, date2, velichina_coupona, coupons, nalog)
print("всё!")








