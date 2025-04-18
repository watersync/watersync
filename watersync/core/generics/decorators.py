from functools import wraps
from django.core.exceptions import FieldError

def filter_by_location(view_func):
    @wraps(view_func)
    def _wrapped_view(self, *args, **kwargs):
        queryset = view_func(self, *args, **kwargs)
        if "location_pk" in self.request.GET:
            try:
                queryset = queryset.filter(location__pk=self.request.GET.get("location_pk"))
            except FieldError:
                queryset = queryset.filter(location_visit__location__pk=self.request.GET.get("location_pk"))
        return queryset
    return _wrapped_view

def filter_by_conditions(*conditions):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, *args, **kwargs):
            queryset = view_func(self, *args, **kwargs)
            for condition in conditions:
                if condition:
                    queryset = queryset.filter(**condition)
            return queryset
        return _wrapped_view
    return decorator