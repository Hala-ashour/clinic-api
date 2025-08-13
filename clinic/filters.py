import django_filters
from .models import Appointment
from django.utils import timezone

class AppointmentFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name='appointment_date', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='appointment_date', lookup_expr='lte')
    doctor = django_filters.NumberFilter(field_name='doctor__id')
    patient = django_filters.NumberFilter(field_name='patient__id')
    status = django_filters.CharFilter(field_name='status')
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'status', 'start_date', 'end_date']