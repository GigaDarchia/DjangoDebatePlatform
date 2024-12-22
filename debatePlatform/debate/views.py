from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import generic, View
from .models import Debate, Argument
from django.db import models
from django.urls import reverse_lazy
from .forms import CreateDebateForm, CreateArgumentForm
from django.http import HttpResponseRedirect


class DebateListing(generic.ListView):
    """
    Represents a view for listing debates.

    This class-based view provides functionality for displaying a list of debates
    with additional context such as participant count. It retrieves the required
    debate data using optimized queryset techniques to minimize database queries.
    The view leverages the Django ListView for rendering a paginated list of debates.

    """
    model = Debate
    queryset = Debate.objects.select_related('category', 'author') \
        .annotate(participant_count=models.Count('participants'))
    template_name = 'debate_list.html'
    context_object_name = 'debates'
    paginate_by = 8


class DebateDetailView(generic.DetailView):
    """
    A view that provides detailed information for a specific debate object.

    This class is used to generate a detailed view of a debate, fetched from
    the database using its primary key. The view assigns necessary objects
    to the context for rendering the details in the template. It uses
    optimized queries to minimize database hits by employing select_related
    and prefetch_related for fetching related fields.

    """
    model = Debate
    context_object_name = 'debate'
    template_name = 'debate_detail.html'
    pk_url_kwarg = 'debate_id'

    def get_queryset(self):
        return Debate.objects.select_related('category', 'author').prefetch_related(
            'participants', 'debate_arguments')


class CreateDebateView(LoginRequiredMixin,generic.CreateView):
    """
    Handles the creation of a new Debate instance through a web form.

    This class-based view is used to render a form for creating a new debate entry,
    validate the form data, associate the logged-in user as the author of the debate,
    and save the data to the database. It requires the user to be logged in.

    """
    model = Debate
    context_object_name = 'debate'
    template_name = 'create_debate.html'
    form_class = CreateDebateForm
    success_url = reverse_lazy('debate_listing')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class JoinDebateView(LoginRequiredMixin, View):
    """
    JoinDebateView allows a logged-in user to join a specific debate by making a POST request.

    This view handles the logic for associating a user with a debate's participant list. If the
    user is not already a participant, they are added to the list of participants for the debate.
    It ensures proper authorization and redirects back to the referring page after processing.

    """
    def post(self, request, *args, **kwargs):
        debate = Debate.objects.get(id=kwargs['debate_id'])

        if request.user not in debate.participants.all():
            debate.participants.add(request.user)

        return redirect(request.META.get('HTTP_REFERER'))


class CreateArgumentView(LoginRequiredMixin, generic.CreateView):
    """
    Allows logged-in users to create a new argument for a specific debate.

    This view handles the argument creation form, assigns the current user as the author,
    links the argument to the specified debate, and redirects back to the previous page
    after successful submission.

    """
    model = Argument
    form_class = CreateArgumentForm
    success_url = reverse_lazy('debate_listing')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.debate = Debate.objects.get(id=self.kwargs['debate_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')
