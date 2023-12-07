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

class MapDoesNotExistInCurrentWarException(Exception):
    """
    Represents an exception where-in a call for something uniquely identified
    for a certain map in a certain war (e.g. icons, labels) is requested but
    there does not exist a row that map for the war in question.

    Indicates that a call was made referring to maps in the current war before
    or in absence of the maps stage of initialization being completed.
    """
    def __init__(
        map_name: str,
        last_known_war: int|None = None
    ) -> None:
        # Change message slightly depending on whether
        # the last_known_war was provided or not
        if last_known_war is not None:
            message = \
                f"A request was made referring to map {map_name}; " \
                f"however, no row exists in the 'maps' table for " \
                f"{map_name} in the current war. The last known war "\
                f"in which this map occurred was {str(last_known_war)}."
        else:
            message = \
                f"A request was made referring to map {map_name}; " \
                f"however, no row exists in the 'maps' table for " \
                f"{map_name} in the current war. The last known war " \
                f"in which this map occurred is unknown."
        
        super().__init__(message)