from django.urls import path, include
from .views import UserRegisterView, UserLoginView, CustomTokenRefreshView, CustomTokenBlacklistView

urlpatterns = [
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', CustomTokenBlacklistView.as_view(), name='token_blacklist'),
]