from rest_framework import serializers
from .models import User, Doctor, Patient, Appointment
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Doctor
        fields = 'all'
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            doctor = Doctor.objects.create(user=user, **validated_data)
            return doctor
        raise serializers.ValidationError(user_serializer.errors)

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Patient
        fields = 'all'
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            patient = Patient.objects.create(user=user, **validated_data)
            return patient
        raise serializers.ValidationError(user_serializer.errors)

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = 'all'
    
    def validate_appointment_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Appointment date must be in the future.")
        return value
    
    def validate(self, data):
        # Check for overlapping appointments
        if 'doctor' in data and 'appointment_date' in data:
            overlapping = Appointment.objects.filter(
                doctor=data['doctor'],
                appointment_date=data['appointment_date'],
                status__in=['PENDING', 'CONFIRMED']
            ).exists()
            
            if overlapping:
                raise serializers.ValidationError(
                    "This doctor already has an appointment at this time."
                )
        return data

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_type'] = user.user_type
        return token