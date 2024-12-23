from django.contrib import admin
from .models import Category, Debate, Argument, Vote


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin Panel Config for Category model."""
    list_display = ("id", "name", "slug")
    list_editable = ("name", "slug")
    ordering = ("id",)

@admin.register(Debate)
class DebateAdmin(admin.ModelAdmin):
    """Admin Panel Config for Debate model."""
    list_display = (
        'title',
        'category',
        'author',
        'created_at',
        'start_time',
        'end_time',
        'status'
    )
    readonly_fields = (
        'created_at',
    )
    list_filter = (
        'status',
    )
    search_fields = (
        'title',
        'description'
    )


@admin.register(Argument)
class ArgumentAdmin(admin.ModelAdmin):
    """Admin Panel Config for Argument model."""
    list_display = (
        'debate',
        'author',
        'side',
        'vote_count',
        'winner',
        'created_at',

    )
    readonly_fields = (
        'created_at',
    )
    list_filter = (
        'winner',
    )
    search_fields = (
        'text',
    )


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Admin Panel Config for Vote model."""
    list_display = (
        "argument",
        "user",
        "created_at"
    )
    readonly_fields = (
        "created_at",
    )
