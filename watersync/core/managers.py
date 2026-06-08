
from watersync.core.generics.managers import (
    LocationWithCountsAndDetailManager,
    ProjectWithCountsManager,
)


class LocationManager(LocationWithCountsAndDetailManager):
    """Manager for Location model with natural key support."""
    
    def get_by_natural_key(self, name):
        return self.get(name=name)


class ProjectManager(ProjectWithCountsManager):
    """Manager for Project model with natural key support."""
    
    def get_by_natural_key(self, name):
        return self.get(name=name)
