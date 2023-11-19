"""
Contains classes and functions for receiving and responding to messages
involving the bot on Discord. These serve as elements of the Discord-facing
UI and are a starting point for feature logic as it's implemented by the bot.

If it's a slash command (/thing) or bang command (!thing), it lives here! :)
"""
from typing import List

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

class Command:
    """
    Parent class for all incoming commands sent by discord users.
    """
    @property
    def command(self) -> str:
        """
        The name of the keyword (/thing or !thing) which executes this Command.

        Returns:
            str: The name of the command which executes this command

        Raises:
            Exception: An exception stating the name of this class, and that it
            doesn't implement the .command attribute as it should.
        """
        raise Exception("Tried to get undefined attribute " +
                        f".command of class {self.__class__.__name__}. " +
                        "Does this class implement its own constructor?")
        return "An exception should have been raised"

    def __init__(self, input_text) -> None:
        self._input_text = input_text


class UserAlreadyHasRoleException(Exception):
    """
    Represents an instance where an attempt was made to give a user
    a role, but that user had already been assigned that role.
    """
    def __init__(self, username: str, role: str) -> None:
        """
        Represents an instance where an attempt was made to give a user
        a role, but that user had already been assigned that role.

        Args:
            username (str): The discord username specified in the request
            role (str): The role which that user was to be assigned
        """
        message = f'User {username} already has the role {role}'
        super().__init__(message)


class UserRoleDoesNotExistException(Exception):
    """
    Represents a case in which a command specified that a role
    which doesn't exist should be assigned to a particular user.
    """
    def __init__(self, username: str, role: str) -> None:
        message = \
            f'Cannot assigned role \'{role}\' to user \'{username}\', ' \
            ' as it does not exist.'
        super().__init__(message)

class UserCommand(Command):
    """
    Represents a single Command issued by the user to modify
    the User table or related tables in some way.

    Supported commands look like:
    !user @username verb [arguments, for, that, verb]
        role
            give
                Ex: "!user @chillCherry role give moderator"
            remove
                Ex: "!user @sussySteve role remove teamster"
        ban
            !user @username ban 'reason for ban'
                Ex: "!user @bigJerk ban 'inappropriate ticket names'"
        tempban
            !user @username tempban num_time_units time_unit @username 
                Ex: "!user @bigJerk tempban 3 days 'ticket claim griefing'"

    """
    

    @property
    def username(self) -> str:
        """Discord username of the user who executed this command"""
        return self._username
    
    @property
    def command(self) -> str:
        return "user"
    
    @property
    def allowed_verbs(self) -> List[str]:
        """The list of verbs to which this command can respond"""
        return [
            "role",
            "ban",
            "tempban"
        ]
    
    def execute(self) -> str:
        """
        Execute the command in question, returning a message to be
        sent back to the user who called the command if successful.

        Raises:
            UserAlreadyHasRoleException:
            Raised if the user already has the specified role

        Returns:
            str: A message to be returned to the user who submitted the command
        """
        raise UserAlreadyHasRoleException()
        pass
    
    def __init__(self, input_text: str) -> None:
        # Call the base constructor which records the original input text
        super().__init__(self, input_text)

        # Split the command by space into a list of tokens, as well
        # as dropping the first one if it's "/user" or "!user"
        all_tokens = input_text.split(" ")
        tokens = \
            all_tokens \
            if all_tokens[0].lower() not in ["!user", "/user"] \
            else all_tokens[1:]
        
        # Identify the target discord user and primary verb
        username = tokens[0]
        verb = tokens[1].lower()

        # Throw an exception if that verb is not in the list of allowed verbs
        if verb not in self.allowed_verbs:
            raise UnsupportedVerbException(
                verb=verb,
                command=self.command,
                message=input_text
            )
