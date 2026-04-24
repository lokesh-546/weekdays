from django import template
from django.utils.timezone import now
from datetime import timedelta

register = template.Library()

@register.filter
def custom_time(value):
    if not value:
        return ''
    diff = now() - value
    
    if diff < timedelta(days=7):
        days = diff.days
        if days == 0: return 'Today'
        return f'{days} days ago'
    
    if diff < timedelta(days=30):
        weeks = diff.days // 7
        return f'{weeks} week' + ('s' if weeks > 1 else '') + ' ago'
    
    if diff < timedelta(days=365):
        months = diff.days // 30
        return f'{months} month' + ('s' if months > 1 else '') + ' ago'
    
    years = diff.days // 365
    return f'{years} year' + ('s' if years > 1 else '') + ' ago'

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0
