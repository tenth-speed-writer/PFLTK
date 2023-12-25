import datetime
from typing import NamedTuple


class CommandData(NamedTuple):
    """
    Represents the relevant information in a single message sent
    to the bot, as it is stored in the application's database.

    Useful for inserting/selecting rows from the commands table and
    exchanging this data outside of the message or command objects.
    """
    id: int
    command: str
    user: int
    guild: str
    channel: str
    created_at: datetime.datetime
    content: str


class Command:
    """
    Parent class for all incoming commands sent by discord users.
    """
    @property
    def id(self) -> int:
        """
        Returns the unique ID of the discord message in which
        this command was originally executed.

        Returns:
            int: The ID of the discord message which called this command.
        """
        return self._id

    @property
    def command(self) -> str:
        """
        Returns the name of the keyword (!thing) which executes this Command.

        Returns:
            str: The name of the command which executes this command
        """
        return self._command
    
    @property
    def user(self) -> int:
        """
        Returns the discord user ID of the user who executed this command.

        Returns:
            int: The ID of the discord user who executed this command.
        """
        return self._user
    
    @property
    def guild(self) -> str:
        """
        Returns the guild (that is, discord server) name for the server in
        which this command was executed.

        Returns:
            str: The server ('guild') in which this command was executed.
        """
        return self._guild
    
    @property
    def channel(self) -> str:
        """
        Returns the name of the channel in which this command was executed.
        Must be paired with the .guild attribute to uniquely identify a
        specific channel.

        Returns:
            str: The name of the channel in which this command was executed.
        """
        return self._channel
    
    @property
    def created_at(self) -> datetime.datetime:
        """
        Returns the datetime on which this message was first created (in UTC)

        Returns:
            datetime.datetime: UTC time when this message was created.
        """
        return self._created_at

    @property
    def content(self) -> str:
        """
        Returns the full text of the message which executed this command.

        Returns:
            str: The text of the message which executed this command.
        """
        return self._content


    #     Raises:
    #         Exception: An exception stating the name of this class, and that it
    #         doesn't implement the .command attribute as it should.
    #     """
    #     raise Exception("Tried to get undefined attribute " +
    #                     f".command of class {self.__class__.__name__}. " +
    #                     "Does this class implement its own constructor?")
    #     return "An exception should have been raised"
    
    # @property
    # def user(self) -> str:
    #     """
    #     The discord username of the user who executed this command.

    #     Returns:
    #         str: The username of the user who executed this command.

    #     Raises:
    #         Exception: An exception stating the name of this class, and that it
    #         doesn't implement the .command attribute as it should.
    #     """
    #     raise Exception("Tried to get undefined attribute " +
    #                     f".user of class {self.__class__.__name__}. " +
    #                     "Does this class implement its own constructor?")

    def __init__(self, input_text) -> None:
        self._input_text = input_text


class UnsupportedVerbException(Exception):
    """
    Represents an instance in which a discord user's command called a
    valid Command type but specified a verb which it doesn't support.
    """
    def __init__(
            self,
            verb: str,
            command: str,
            message: str) -> None:
        """
        Represents an instance in which a discord user's command called a
        valid Command type but specified a verb which it doesn't support.

        May happen because of missing features or simply because of typos.

        Args:
            verb (str): The name of the verb the user tried to call
            command (str): The command from which this error was thrown
            message (str): The user's full discord message as the Command received it
        """
        message = \
            f'Unsupported verb \'{verb}\' for command \'{command}\''
        super().__init__(message)