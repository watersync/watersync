class InterfaceModelTemplate:
    """Process the dictionaries of model fields' signatures and their corresponding verbose names for given view type.

    When models inherit this mixin, those lists are available as properties in templates.
    """

    _list_view_fields: dict = None
    _detail_view_fields: dict = None

    def _return_items(self, fields):
        """Returns a list of tuples with field names and their corresponding verbose names."""
        return [
            (field_name_verb, getattr(self, field))
            for field_name_verb, field in fields.items()
        ]

    @property
    def detail_view_items(self):
        """Process the dictionary of detail view fields."""
        return self._return_items(self._detail_view_fields)

    @property
    def list_view_items(self):
        """Process the dictionary of list view fields."""
        return self._return_items(self._list_view_fields)