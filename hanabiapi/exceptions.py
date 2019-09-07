"""Module to define exceptions used in the Hanabi API."""


class DatabaseError(Exception):
    """Top level exception manager for databases."""

    def __init__(self, message=None, *args, **kwargs):
        """
        Initialize a ``DatabaseError`` exception.

        :param message: A helpful message the exception should contain.
        :param args: Any additional args to attach to the exception.
        :param kwargs: Any additional kwargs to attach to the exception.
        """
        self.db = kwargs.pop('db', 'DB not given')
        if message is None:
            self.message = self.__class__.__name__
        super().__init__(message=self.message, db=self.db, *args, **kwargs)


class NotFound(DatabaseError):
    """Raised if a generic item does not exist."""

    def __init__(self, _type, message=None, *args, **kwargs):
        """
        Initialize a generic ``NotFound`` exception.

        :param _type: The type of item that was not found (e.g. ``user``)
        :param message: A helpful message the exception should contain.
        :param args: Any additional args to attach to the exception.
        :param kwargs: Any additional kwargs to attach to the exception.
        """
        self.message = message
        if self.message is None:
            self.message = kwargs.pop('message', 'No ' + _type + ' found')
        super().__init__(message=self.message, *args, **kwargs)


class GameNotFound(NotFound):
    """Raised if a game cannot be found."""

    def __init__(self, message=None, *args, **kwargs):
        """
        Initialize a ``GameNotFound`` exception.

        :param message: A helpful message the exception should contain.
        :param args: Any additional args to attach to the exception.
        :param kwargs: Any additional kwargs to attach to the exception.
        """
        super().__init__('game', message=message, *args, **kwargs)
