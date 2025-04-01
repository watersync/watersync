from functools import wraps


def filter_by_location(view_func):
    @wraps(view_func)
    def _wrapped_view(self, *args, **kwargs):
        queryset = view_func(self, *args, **kwargs)
        if "location_pk" in self.request.GET:
            queryset = queryset.filter(location__pk=self.request.GET.get("location_pk"))
        return queryset
    return _wrapped_view