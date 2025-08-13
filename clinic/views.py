from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Doctor, Patient, Appointment
from .serializers import (
    UserSerializer, DoctorSerializer, PatientSerializer, 
    AppointmentSerializer, CustomTokenObtainPairSerializer
)
from .permissions import (
    IsAdmin, IsDoctor, IsPatient, IsDoctorOrAdmin, 
    IsPatientOrAdmin, IsAppointmentOwner
)
from .filters import AppointmentFilter
from django_filters.rest_framework import DjangoFilterBackend

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        if self.request.user.user_type == 'DOCTOR':
            return Doctor.objects.filter(user=self.request.user)
        return super().get_queryset()

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        if self.request.user.user_type == 'PATIENT':
            return Patient.objects.filter(user=self.request.user)
        return super().get_queryset()

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AppointmentFilter
    permission_classes = [IsAuthenticated, IsAppointmentOwner]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'ADMIN':
            return super().get_queryset()
        elif user.user_type == 'DOCTOR':
            return Appointment.objects.filter(doctor__user=user)
        elif user.user_type == 'PATIENT':
            return Appointment.objects.filter(patient__user=user)
        return Appointment.objects.none()

    def create(self, request, *args, **kwargs):
        if request.user.user_type != 'PATIENT':
            return Response(
                {"detail": "Only patients can create appointments."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Ensure the patient is the requesting user
        request.data['patient'] = request.user.patient_profile.id
        return super().create(request, *args, **kwargs)
