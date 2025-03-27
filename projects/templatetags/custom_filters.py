from django import template
from datetime import datetime

register = template.Library()

@register.filter
def get_sequence(path):
    """Extract the sequence part from the folder path."""
    parts = path.split("/")
    return parts[1] if len(parts) > 1 else ""

@register.filter
def get_shot(path):
    """Extract the shot part from the folder path."""
    parts = path.split("/")
    return parts[2] if len(parts) > 2 else ""

@register.filter
def format_iso_date(value):
    if value is None:
        return '' 
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return value
