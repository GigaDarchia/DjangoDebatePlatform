from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from .forms import SignUpForm
from .models import User

class ProfileView(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = 'profile.html'
    slug_field = 'slug'
    slug_url_kwarg = 'user_slug'


class LogInView(LoginView):
    template_name = 'login.html'
    authentication_form = AuthenticationForm
    next_page = 'debate_listing'


class RegisterView(generic.CreateView):
    template_name = 'register.html'
    model = User
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()

        print(f"User create successfully: {user}")
        return super().form_valid(form)

