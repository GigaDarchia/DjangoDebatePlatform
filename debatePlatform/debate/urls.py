from django.urls import path
from django.views.decorators.cache import cache_page

from .views import (DebateListing,
                    DebateDetailView,
                    CreateDebateView,
                    JoinDebateView,
                    CreateArgumentView,
                    HomeView,
                    VoteView,
                    SearchView,
                    CategoryView,
                    FilterView)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('debates/', DebateListing.as_view(), name='debate_listing'),
    path('debates/<int:debate_id>/', DebateDetailView.as_view(), name='debate_detail'),
    path('debates/create/', CreateDebateView.as_view(), name='create_debate'),
    path('<int:debate_id>/join/', JoinDebateView.as_view(), name='join'),
    path('<int:debate_id>/create_argument/', CreateArgumentView.as_view(), name='create_argument'),
    path('<int:argument_id>/vote/', VoteView.as_view(), name='vote'),
    path('search/', SearchView.as_view(), name='search'),
    path('category/<slug:slug>/', CategoryView.as_view(), name='category'),
    path('filter/', FilterView.as_view(), name='filter'),
]