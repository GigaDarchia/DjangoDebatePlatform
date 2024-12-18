from django_filters import rest_framework as filters
from debate.models import Debate

class DebateFilter(filters.FilterSet):
    category = filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Debate
        fields = ['category']