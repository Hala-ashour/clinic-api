from django.contrib import admin

from clinic.models import Appointment, Doctor, Patient, User

# Register your models here.
admin.site.register(User)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)