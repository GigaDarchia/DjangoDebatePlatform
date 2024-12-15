from django.urls import path, include
from .views import UserRegisterView, UserLoginView

urlpatterns = [
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
]