"""Contains exceptions shared between the database interaction methods"""

class MultipleUniqueRowsException(Exception):
    """
    Represents an exception where a query which should have returned a
    single unique row instead returned multiple rows.
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
class UniqueRowNotFoundException(Exception):
    """
    Represents an exception where a query which should have returned a
    single row's worth of data based on its primary key or other unique
    identifier instead returned no rows.
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class UniqueRowAlreadyExistsException(Exception):
    """
    Represents an exception where an attempt is made to insert a
    row with a unique value which already exists in that table.
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NoDataReturnedException(Exception):
    """
    Represents an exception where a query which should have returned data
    if the app is in operating order instead returned nothing. This is
    primarily used for data that should have been populated when the
    application launched, rather than just returned when a table is empty.
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)