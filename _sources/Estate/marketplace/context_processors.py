from .models import Inquiry, Property, Transaction

def global_stats(request):
    return {'global_total_properties':Property.objects.count(),'global_available_properties':Property.objects.filter(status=Property.Status.APPROVED).count(),'global_sold_properties':Property.objects.filter(status=Property.Status.SOLD).count(),'global_inquiries':Inquiry.objects.count(),'global_completed_transactions':Transaction.objects.filter(status=Transaction.Status.COMPLETED).count()}
