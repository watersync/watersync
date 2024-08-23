from django.contrib import admin

from django.contrib import admin
from .models import Location, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('name', 'user')
    search_fields = ('name',)  # Fields to search by
    list_filter = ('user',)  # Add filters in the right sidebar


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('name', 'added_by')
    search_fields = ('name',)  # Fields to search by
    list_filter = ('added_by',)
