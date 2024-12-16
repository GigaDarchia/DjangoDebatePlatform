from django.urls import path, include
from .views import UserRegisterView, UserLoginView, CustomTokenRefreshView, CustomTokenBlacklistView, CategoryListing, DebateViewSet, ArgumentViewSet, \
    VoteView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('debates', DebateViewSet, basename='debates')
router.register('arguments', ArgumentViewSet, basename='arguments')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', CustomTokenBlacklistView.as_view(), name='token_blacklist'),
    path('categories/', CategoryListing.as_view(), name='categories'),
    path('vote/', VoteView.as_view(), name='vote'),
]