# Create a file: traveling_agency/templatetags/math_filters.py

from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide the value by the argument."""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    """Subtract the argument from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """Calculate percentage of value from total."""
    try:
        if float(total) == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError):
        return 0

@register.filter
def currency(value):
    """Format number as currency with commas."""
    try:
        return "KSh {:,.0f}".format(float(value))
    except (ValueError, TypeError):
        return "KSh 0"

@register.filter
def progress_width(value, max_value=100):
    """Calculate progress bar width percentage."""
    try:
        if max_value == 0:
            return 0
        percentage = (float(value) / float(max_value)) * 100
        return min(percentage, 100)  # Cap at 100%
    except (ValueError, TypeError):
        return 0