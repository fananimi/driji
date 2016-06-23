from django import template

register = template.Library()

@register.filter('get_value')
def get_value(dict_data, key):
    """
    usage example {{ your_dict|get_value:your_key }}
    """
    if key:
        key = str(key)
        return dict_data.get(key)
