from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import ValidationError
from django.utils import timezone

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    groups = models.ManyToManyField(Group, related_name='clinic_users')
    user_permissions = models.ManyToManyField(Permission, related_name='clinic_users_permissions')

    def str(self):
        return f"{self.username} ({self.get_user_type_display()})"

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialty = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    years_of_experience = models.PositiveIntegerField()
    
    def str(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialty}"

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=5)
    allergies = models.TextField(blank=True)
    
    def str(self):
        return f"{self.user.get_full_name()}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date']
    
    def str(self):
        return f"{self.patient} with {self.doctor} on {self.appointment_date}"
    
    def clean(self):
        if self.appointment_date <= timezone.now():
            raise ValidationError("Appointment date must be in the future.")
        
        # Check for overlapping appointments
        overlapping_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date=self.appointment_date,
            status__in=['PENDING', 'CONFIRMED']
        ).exclude(pk=self.pk)
        
        if overlapping_appointments.exists():
            raise ValidationError("This doctor already has an appointment at this time.")