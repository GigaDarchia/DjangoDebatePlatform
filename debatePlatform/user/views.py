from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from .forms import SignUpForm
from .models import User

class ProfileView(generic.DetailView):
    model = User
    template_name = 'profile.html'
    slug_field = 'slug'
    slug_url_kwarg = 'user_slug'
    context_object_name = 'profile_user'
    queryset = User.objects.prefetch_related('author_debates', 'participated_debates')


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

class UpdateProfilePicture(generic.UpdateView):
    model = User
    fields = ['profile_picture']
    success_url = reverse_lazy('home')
    pk_url_kwarg = 'user_slug'

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')