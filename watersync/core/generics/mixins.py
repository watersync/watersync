from django.utils.timezone import now


class ModelTemplateInterface:
    """Add attributes that are used in generic templates."""

    _list_view_fields: dict = None
    _detail_view_fields: dict = None

    def _return_items(self, fields):
        """
        Helper method that returns a list of tuples containing field names and their corresponding values.
        """
        return [
            (field_name_verb, getattr(self, field))
            for field_name_verb, field in fields.items()
        ]

    @property
    def detail_view_items(self):
        """
        Property that returns a list of tuples containing field names and their corresponding values.
        """
        return self._return_items(self._detail_view_fields)

    @property
    def list_view_items(self):
        """
        Property that returns a list of tuples containing field names and their corresponding values.
        """
        return self._return_items(self._list_view_fields)


class SimpleHistorySetup:
    """
    Mixin class that provides a simple history setup for the models.

    You still need to add the history field to the model:

        >>> history = HistoricalRecords()
    """
    __history_date = None

    @property
    def _history_date(self):
        return self.__history_date or now()

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value
