from django.contrib import admin

from .models import Location, Project

# just adding a commet to see something


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ("name",)
    search_fields = ("name",)  # Fields to search by
    list_filter = ("user",)  # Add filters in the right sidebar


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ("name",)
    search_fields = ("name",)  # Fields to search by
    list_filter = ("user",)
