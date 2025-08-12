from django.utils.timezone import now


class SetupSimpleHistory:
    """Provides a simple history setup for models.

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
