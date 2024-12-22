from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView
from .views import ProfileView, LogInView, RegisterView

urlpatterns = [
    path('profile/<slug:user_slug>/', ProfileView.as_view(), name='profile'),
    path('login/', LogInView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]
