from .models import Category
from django.core.cache import cache

def category_processor(request):
    categories = cache.get('categories')
    if not categories:
        categories = Category.objects.all()
        cache.set('categories', categories, 60*60)
    return {'categories': categories}

