from django import template

register = template.Library()

@register.filter
def first_name(value):
    """Get first name from full name"""
    if not value:
        return ''
    return value.split(' ', 1)[0]

@register.filter
def last_name(value):
    """Get last name from full name"""
    if not value:
        return ''
    parts = value.split(' ', 1)
    return parts[1] if len(parts) > 1 else ''
