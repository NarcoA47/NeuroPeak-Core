from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from .models import LecturerProfile, StudentProfile
from .serializers import (UserSerializer, LecturerProfileSerializer, StudentProfileSerializer, CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer)

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'register']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Custom registration endpoint that defaults to student role"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(user_type=User.UserType.STUDENT)
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LecturerProfileViewSet(viewsets.ModelViewSet):
    queryset = LecturerProfile.objects.all()
    serializer_class = LecturerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        if self.request.user.user_type == User.UserType.LECTURER:
            serializer.save(user=self.request.user)

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        if self.request.user.user_type == User.UserType.STUDENT:
            serializer.save(user=self.request.user)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer