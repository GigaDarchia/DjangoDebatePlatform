from django.contrib import admin
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Debate)
class DebateAdmin(admin.ModelAdmin):
    pass

@admin.register(Argument)
class ArgumentAdmin(admin.ModelAdmin):
    pass

@admin.register(Vote)
class Vote(admin.ModelAdmin):
    pass