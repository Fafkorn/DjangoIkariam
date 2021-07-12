from django import template
import re

register = template.Library()


@register.filter
def get_pos(position, page_num):
    try:
        return int(page_num-1) * 100 + int(position)
    except (ValueError, ZeroDivisionError):
        return None


@register.filter
def get_time(seconds):
    minutes = int(seconds/60)
    seconds = seconds % 60
    if minutes > 0 and seconds > 0:
        return str(minutes) + 'm ' + str(seconds) + 's'
    elif minutes > 0 and seconds == 0:
        return str(minutes) + 'm'
    elif minutes == 0 and seconds > 0:
        return str(seconds) + 's'
    else:
        return "error"


@register.filter
def number_commas(number):
    return re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1,", "%d" % number)


@register.filter(name='times')
def times(number):
    return range(number)
