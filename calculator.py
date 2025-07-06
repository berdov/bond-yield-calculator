from datetime import datetime, timedelta
from prettytable import PrettyTable



def create_table():
    table = PrettyTable()
    table.field_names = ["Номер купона", "Дата выплаты", "Текущая цена бумаги", "Остаток на счете", "Оценочная стоимость", "Число бумаг", "Комиссия"]
    table.align = "c"  
    table.float_format = ".2"  
    return table

def print_table(table):
    print("\nРезультаты купонов:")
    print(table)

def calc(balance, price, date1, date2, velichina_coupona, coupons, nalog, comission, type_of_increase, current_coupon):
    result_comission = 0
    start_balance = balance
    difference = date1 - date2
    dni = difference.days
    frac = dni / 365
    amount_of_coupons = frac * coupons
    price_increase = (1000 - price) / amount_of_coupons
    price_multiply = (1000/price)**(1/(amount_of_coupons))
    amount_of_bonds = int(balance / (current_coupon + price + price*comission))
    balance -= amount_of_bonds * (current_coupon + price + price*comission)
    date_of_coupon = date2
    table = create_table()
    table.add_row([0, date_of_coupon.strftime("%d %m %Y"), f"{price:.2f}", f"{balance:.2f}", f"{start_balance:.2f}", amount_of_bonds, comission*price*amount_of_bonds])
    result_comission += comission*price*amount_of_bonds
    for i in range(1, int(amount_of_coupons) + 2):
        if type_of_increase == 'л':
            if i == int(amount_of_coupons) + 1:
                price = 1000
                date_of_coupon = date1
            elif i == 1:
                price = 1000 - price_increase * int(amount_of_coupons)
                date_of_coupon = date1 - timedelta(days=int(amount_of_coupons) * 365 / coupons)
            else:
                price += price_increase
                date_of_coupon += timedelta(days=(365 / coupons))
            
        else:
            if i == int(amount_of_coupons) + 1:
                price = 1000
                date_of_coupon = date1
            elif i == 1:
                price *= price_multiply
                date_of_coupon = date1 - timedelta(days=int(amount_of_coupons) * 365 / coupons)
            else:
                price *= price_multiply
                date_of_coupon += timedelta(days=(365 / coupons))
        balance += (velichina_coupona * amount_of_bonds)
        skolko_dokupim = int(balance / (price + price*comission))
        amount_of_bonds += skolko_dokupim
        balance -= (skolko_dokupim * price * (1+comission))
        estimated_value = price * amount_of_bonds + balance
        result_comission+= skolko_dokupim*price*comission
        table.add_row([i, date_of_coupon.strftime("%d %m %Y"), f"{price:.2f}", f"{balance:.2f}", f"{estimated_value:.2f}", amount_of_bonds, skolko_dokupim*price*comission])
    print_table(table)
    result_of_investment = price * amount_of_bonds + balance
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

