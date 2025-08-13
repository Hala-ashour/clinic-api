from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'ADMIN'

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'DOCTOR'

class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'PATIENT'

class IsDoctorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type in ['DOCTOR', 'ADMIN']

class IsPatientOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type in ['PATIENT', 'ADMIN']

class IsAppointmentOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'PATIENT':
            return obj.patient.user == request.user
        elif request.user.user_type == 'DOCTOR':
            return obj.doctor.user == request.user
        return True
    