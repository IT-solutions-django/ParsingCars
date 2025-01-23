currency = {
    'krw': 0.069,
    'eur': 103
}


def recycling_fee(year, engine_capacity, fuel_type):
    base_bid = 20000
    if year <= 3:
        if fuel_type == 'E':
            k = 0.17
        else:
            if engine_capacity <= 3000:
                k = 0.17
            elif 3001 <= engine_capacity <= 3500:
                k = 107.67
            elif engine_capacity >= 3501:
                k = 137.11
    else:
        if fuel_type == 'E':
            k = 0.26
        else:
            if engine_capacity <= 3000:
                k = 0.26
            elif 3001 <= engine_capacity <= 3500:
                k = 165.84
            elif engine_capacity >= 3501:
                k = 180.24

    recycling = base_bid * k

    return recycling


def customs_clearance(price_rus):
    if price_rus <= 200000:
        cost = 1067
    elif 20000 < price_rus <= 450000:
        cost = 2134
    elif 450000 < price_rus <= 1200000:
        cost = 4269
    elif 1200000 < price_rus <= 2700000:
        cost = 11746
    elif 2700000 < price_rus <= 4200000:
        cost = 16524
    elif 4200000 < price_rus <= 5500000:
        cost = 21344
    elif 5500000 < price_rus <= 7000000:
        cost = 27540
    else:
        cost = 30000

    return cost


def custom_duty(price, eng_v, year, fuel_type):
    if fuel_type == 'E':
        duty = (price / 100) * 15
    else:
        if year < 3:
            if price < currency['eur'] * 8500:
                duty = 2.5 * currency['eur'] * eng_v
            elif currency['eur'] * 8500 <= price < currency['eur'] * 16700:
                duty = 3.5 * currency['eur'] * eng_v
            elif currency['eur'] * 16700 <= price < currency['eur'] * 42300:
                duty = 5.5 * currency['eur'] * eng_v
            elif currency['eur'] * 42300 <= price < currency['eur'] * 84500:
                duty = 7.5 * currency['eur'] * eng_v
            elif currency['eur'] * 84500 <= price < currency['eur'] * 169000:
                duty = 15 * currency['eur'] * eng_v
            else:
                duty = 20 * currency['eur'] * eng_v
        elif 3 <= year <= 5:
            if eng_v <= 1000:
                duty = 1.5 * currency['eur'] * eng_v
            elif 1001 <= eng_v <= 1500:
                duty = 1.7 * currency['eur'] * eng_v
            elif 1501 <= eng_v <= 1800:
                duty = 2.5 * currency['eur'] * eng_v
            elif 1801 <= eng_v <= 2300:
                duty = 2.7 * currency['eur'] * eng_v
            elif 2301 <= eng_v <= 3000:
                duty = 3 * currency['eur'] * eng_v
            else:
                duty = 3.6 * currency['eur'] * eng_v
        else:
            if eng_v <= 1000:
                duty = 3 * currency['eur'] * eng_v
            elif 1001 <= eng_v <= 1500:
                duty = 3.2 * currency['eur'] * eng_v
            elif 1501 <= eng_v <= 1800:
                duty = 3.5 * currency['eur'] * eng_v
            elif 1801 <= eng_v <= 2300:
                duty = 4.8 * currency['eur'] * eng_v
            elif 2301 <= eng_v <= 3000:
                duty = 5 * currency['eur'] * eng_v
            else:
                duty = 5.7 * currency['eur'] * eng_v

    return duty


def price_cars(year, engine_capacity, fuel_type, price_rus):
    finish_price = recycling_fee(year, engine_capacity, fuel_type) + customs_clearance(
        price_rus * currency['krw']) + custom_duty(
        price_rus * currency['krw'], engine_capacity, year, fuel_type) + (price_rus * currency['krw'])

    return finish_price
