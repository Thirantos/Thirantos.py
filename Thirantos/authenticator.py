import secrets
from abc import ABC, abstractmethod
from time import time

class Authenticator(ABC):
    """
    Abstract base class for an authenticator.
    """

    @abstractmethod
    def __init__(self, **kwargs):
        """
        Initialize the authenticator with given keyword arguments.
        """
        pass

    @abstractmethod
    def authenticate(self, password: str, **kwargs) -> str:
        """
        Authenticate the user with the given password.

        Args:
            password (str): The password to authenticate.

        Returns:
            str: A token if authentication is successful, otherwise an empty string.
        """
        pass

    @abstractmethod
    def use_token(self, token: str, **kwargs) -> bool:
        """
        Use the given token to verify authentication.

        Args:
            token (str): The token to verify.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        pass

    @abstractmethod
    def update_tokens(self) -> None:
        """
        Update the tokens, removing any that have expired.
        """
        pass

class SinglePassAuth(Authenticator):
    """
    Single password authenticator implementation.
    """

    def __init__(self, max_login_time: int, password: str):
        """
        Initialize the SinglePassAuth with a maximum login time and password.

        Args:
            max_login_time (int): The maximum time a token is valid.
            password (str): The password for authentication.
        """
        self.max_login_time = int(max_login_time)
        self.password = password
        self.tokens: dict[str, int] = {}

    def authenticate(self, password: str, **kwargs) -> str:
        """
        Authenticate the user with the given password.

        Args:
            password (str): The password to authenticate.

        Returns:
            str: A token if authentication is successful, otherwise an empty string.
        """
        token: str = ''
        if password == self.password:
            cur_time = int(time())
            token = secrets.token_urlsafe(32)
            self.tokens[token] = cur_time
        return token

    def use_token(self, token: str, **kwargs) -> bool:
        """
        Use the given token to verify authentication.

        Args:
            token (str): The token to verify.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        if token not in self.tokens:
            return False

        if time() - self.tokens[token] > self.max_login_time:
            self.tokens.pop(token)
            return False

        self.tokens[token] = int(time())
        return True

    def update_tokens(self) -> None:
        """
        Update the tokens, removing any that have expired.
        """
        for t in self.tokens:
            if time() - self.tokens[t] > self.max_login_time:
                self.tokens.pop(t)