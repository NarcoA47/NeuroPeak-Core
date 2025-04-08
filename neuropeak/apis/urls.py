# urls.py
from django.urls import path
from users.views import (UserViewSet,LecturerProfileViewSet,StudentProfileViewSet,CustomTokenObtainPairView,CustomTokenRefreshView)

urlpatterns = [
    # Token endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # User CRUD
    path('users/', UserViewSet.as_view({
        'post': 'create',
        'get': 'list'
    }), name='user-list'),
    path('users/<int:pk>/', UserViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='user-detail'),
    path('register/', UserViewSet.as_view({'post': 'register'}), name='register'),
    
    # Lecturer Profile CRUD
    path('lecturers/', LecturerProfileViewSet.as_view({
        'post': 'create',
        'get': 'list'
    }), name='lecturer-list'),
    path('lecturers/<int:pk>/', LecturerProfileViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='lecturer-detail'),
    
    # Student Profile CRUD
    path('students/', StudentProfileViewSet.as_view({
        'post': 'create',
        'get': 'list'
    }), name='student-list'),
    path('students/<int:pk>/', StudentProfileViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='student-detail'),
]