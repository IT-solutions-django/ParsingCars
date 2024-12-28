def recycling_fee(year, engine_capacity):
    base_bid = 20000
    if year <= 3:
        if engine_capacity <= 3000:
            k = 0.17
        elif 3001 <= engine_capacity <= 3500:
            k = 89.73
        elif engine_capacity >= 3501:
            k = 114.26
    else:
        if engine_capacity <= 3000:
            k = 0.26
        elif 3001 <= engine_capacity <= 3500:
            k = 137.36
        elif engine_capacity >= 3501:
            k = 150.2

    recycling = base_bid * k

    return recycling


def customs_duty(price_rus):
    if price_rus <= 200000:
        cost = 775
    elif 20000 < price_rus <= 450000:
        cost = 1550
    elif 450000 < price_rus <= 1200000:
        cost = 3100
    elif 1200000 < price_rus <= 2700000:
        cost = 8530
    elif 2700000 < price_rus <= 4200000:
        cost = 12000
    elif 4200000 < price_rus <= 5500000:
        cost = 15500
    elif 5500000 < price_rus <= 7000000:
        cost = 20000
    elif 7000000 < price_rus <= 8000000:
        cost = 23000
    elif 8000000 < price_rus <= 9000000:
        cost = 25000
    elif 9000000 < price_rus <= 10000000:
        cost = 27000
    else:
        cost = 30000

    return cost


def price_cars():
    pass
