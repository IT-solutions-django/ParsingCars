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
