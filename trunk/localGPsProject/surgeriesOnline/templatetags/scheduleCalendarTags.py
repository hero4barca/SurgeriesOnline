from django import template

register = template.Library()

@register.filter(name='is_weekend')
def is_weekend(value,week):
    if week.index(value) == 6 or week.index(value)== 5:
        return True
    else:
        return False

@register.filter(name='day_index')
def day_index(value,week):
        return week.index(value)


@register.filter(name='day_class')
def day_class(value,week):
    if week.index(value) == 6 or week.index(value)== 5:
        return "weekend"
    else:
        return "day"

@register.filter(name='before_today')
def before_today(value,week):
    if week.index(value) == 6 or week.index(value)== 5:
        return "weekend"
    else:
        return "day"

@register.filter(name='month_name')
def month_name(value):
    if value == 1:
        return "Jan"
    elif value == 2:
        return "Feb"
    elif value == 3:
        return "March"
    elif value == 4:
        return  "April"
    elif value == 5:
        return "May"
    elif value == 6:
        return "June"
    elif value == 7:
        return  "July"
    elif value ==8:
        return  "Aug"
    elif value == 9:
        return "Sept"
    elif value == 10:
        return  "Oct"
    elif value == 11:
        return  "Nov"
    else:
        return "Dec"


