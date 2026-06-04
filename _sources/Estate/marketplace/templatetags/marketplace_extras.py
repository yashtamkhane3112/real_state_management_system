from django import template
from marketplace.utils import money
register=template.Library()
@register.filter
def rupee(value): return money(value)
@register.filter
def status_class(value):
    v=str(value or '').upper()
    if v in {'APPROVED','COMPLETED','RESPONDED'}: return 'status-available'
    if v=='SOLD': return 'status-sold'
    if v in {'PENDING','IN_PROGRESS','NEW'}: return 'status-pending'
    if v in {'REJECTED','CANCELLED'}: return 'status-rejected'
    if v=='VIEWED': return 'status-viewed'
    return 'status-default'
