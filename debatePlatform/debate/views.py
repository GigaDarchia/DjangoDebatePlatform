from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import generic, View
from .models import Debate, Argument, Vote, Category
from user.models import User
from django.db import models
from django.urls import reverse_lazy
from .forms import CreateDebateForm, CreateArgumentForm, SearchForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db import transaction


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
        .annotate(participant_count=models.Count('participants')) \
        .order_by('-participant_count', '-created_at')
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


class CreateDebateView(LoginRequiredMixin, generic.CreateView):
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
    login_url = reverse_lazy('login')

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
    login_url = reverse_lazy('login')

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
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        debate = Debate.objects.get(id=self.kwargs['debate_id'])
        if debate.status != "Ongoing":
            messages.error(self.request, "You can't create an argument. The debate is not ongoing.")
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', self.success_url))

        form.instance.author = self.request.user
        form.instance.debate = debate

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')


class HomeView(generic.TemplateView):
    """
    Represents the Home view for displaying a template with context data.

    This class demonstrates the use of Django's generic TemplateView to render
    a home page. The context data includes a curated list of debates and user
    leaderboards based on certain conditions.

    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        users = User.objects.all()
        debates = Debate.objects.prefetch_related('participants').select_related('category').annotate(
            participant_count=models.Count('participants'))
        debates = list(debates)

        context = super().get_context_data(**kwargs)

        context['trending_debates'] = sorted(
            (debate for debate in debates if debate.status in ('Scheduled', 'Ongoing')), key=lambda d: d.created_at,
            reverse=True)[:5]
        context['latest_debates'] = sorted((debate for debate in debates if debate.status == "Scheduled"),
                                           key=lambda d: d.created_at)[:5]
        context['active_debates'] = sorted((debate for debate in debates if debate.status == "Ongoing"),
                                           key=lambda d: d.created_at)[:5]
        context['xp_leaderboard'] = users.order_by('-xp')[:10]
        context['win_leaderboard'] = users.order_by('-wins')[:10]
        return context


class VoteView(LoginRequiredMixin, View):
    """
    Handles voting actions for arguments.

    This class-based view ensures that only logged-in users can interact with the voting
    system. It allows users to either upvote or remove their vote from an argument. The
    vote count and the associated author's experience points (xp) are updated accordingly
    based on the user's action.

    """
    login_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        argument = Argument.objects.get(id=kwargs['argument_id'])

        vote = Vote.objects.filter(user=request.user, argument=argument)

        if vote:
            vote.delete()
            argument.vote_count = models.F('vote_count') - 1
            User.objects.filter(id=argument.author.id).update(xp=models.F('xp') - 2)
            argument.save()
            messages.success(request, "Your vote has been removed!")
            return redirect(request.META.get('HTTP_REFERER'))

        with transaction.atomic():
            Vote.objects.create(user=request.user, argument=argument)
            argument.vote_count = models.F('vote_count') + 1
            User.objects.filter(id=argument.author.id).update(xp=models.F('xp') + 2)
            argument.save()

        messages.success(request, "Your vote has been submitted!")
        return redirect(request.META.get('HTTP_REFERER'))


class SearchView(generic.ListView):
    """
    SearchView provides functionality to display a list of debates filtered
    by a search query. It uses pagination and a custom form for search input.

    This view handles the logic to process a search query, filter debates by their
    title or description, and return the results with additional context information
    such as form validation. It organizes debates by the number of participants and
    creation date.

    """
    model = Debate
    template_name = 'debate_list.html'
    context_object_name = 'debates'
    paginate_by = 8
    form_class = SearchForm

    def get_queryset(self):
        form = self.form_class(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            return (Debate.objects.filter(
                models.Q(title__contains=query) | models.Q(description__contains=query))
                    .select_related('category', 'author')
                    .annotate(participant_count=models.Count('participants'))
                    .order_by('-participant_count', '-created_at'))
        return Debate.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.form_class(self.request.GET)
        context['form'] = form if form.is_valid() else self.form_class()
        return context


class CategoryView(generic.ListView):
    """
    Handles the display and pagination of debates by category.

    This class-based view is responsible for listing debates that belong to a
    specific category. It fetches debates from the database, applies the necessary
    filters, annotations, and orders them by popularity and creation date. The
    results are displayed in a paginated format in the specified template.

    """
    model = Debate
    template_name = 'debate_list.html'
    paginate_by = 8
    context_object_name = 'debates'

    def get_queryset(self):
        category = Category.objects.get(slug=self.kwargs['slug'])
        return (Debate.objects.filter(category=category).select_related('category', 'author')
                .annotate(participant_count=models.Count('participants'))
                .order_by('-participant_count', '-created_at'))


class FilterView(generic.ListView):
    """
    FilterView is a Django generic ListView that is used to display a list of Debates
    with optional filtering based on status and category.

    This view allows displaying debates with associated additional context, including
    participant counts and sorted order based on specific attributes. Users can also
    paginate through the list of debates.

    """
    model = Debate
    template_name = 'debate_list.html'
    paginate_by = 8
    context_object_name = 'debates'

    def get_queryset(self):
        status = self.request.GET.get('status')
        category_id = self.request.GET.get('category')
        debates = (Debate.objects.select_related('category', 'author')
                   .annotate(participant_count=models.Count('participants'))
                   .order_by('-participant_count', '-created_at'))

        if status and status != "All":
            debates = debates.filter(status=status)

        if category_id and category_id != "All":
            category_id = int(category_id)
            debates = debates.filter(category_id=category_id)

        return debates
