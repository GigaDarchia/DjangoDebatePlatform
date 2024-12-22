from django.urls import path
from .views import DebateListing, DebateDetailView, CreateDebateView, JoinDebateView, CreateArgumentView

urlpatterns = [
    path('listing/', DebateListing.as_view(), name='debate_listing'),
    path('<int:debate_id>/', DebateDetailView.as_view(), name='debate_detail'),
    path('create/', CreateDebateView.as_view(), name='create_debate'),
    path('<int:debate_id>/join/', JoinDebateView.as_view(), name='join'),
    path('<int:debate_id>/create_argument/', CreateArgumentView.as_view(), name='create_argument'),
]