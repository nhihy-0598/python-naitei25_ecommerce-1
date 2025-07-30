from django import template

register = template.Library()

@register.filter(name='price_format')
def price_format(value):
    try:
        return f"{float(value):.2f}"
    except (ValueError, TypeError):
        return "0.00"
