import re
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def clean_markdown(value):
    if not value:
        return value
    value = re.sub(r'#{1,6}\s*', '', value)
    value = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', value)
    return value
