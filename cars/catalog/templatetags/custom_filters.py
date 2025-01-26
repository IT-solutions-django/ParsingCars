from django import template

register = template.Library()


@register.filter
def format_number(value):
    try:
        value = int(float(value))

        formatted_value = f"{value:,}".replace(',', ' ')

        return formatted_value
    except (ValueError, TypeError):
        return value


@register.filter
def divide(value, divisor):
    try:
        return float(value) / divisor
    except (ValueError, TypeError):
        return None


@register.filter
def fuel_type(value):
    if value == 'G':
        return 'Бензин'
    elif value == 'D':
        return 'Дизель'
    elif value == 'E':
        return 'Электрический'
    elif value == 'L':
        return 'Сниженный газ'
    elif value == 'H':
        return 'Гибридный'
    else:
        return value


@register.filter
def kpp(value):
    if value in ('AT', '', 'CVT', 'SEMIAT', '세미', '지역:'):
        return 'Автомат'
    elif value == 'MT':
        return 'Механика'
    else:
        return value


@register.filter
def eng_v(value):
    return f'{value / 1000:.1f}'


@register.filter
def krw_price(value):
    if str(value).isalpha():
        return value
    else:
        return f'{value} 백만원'
