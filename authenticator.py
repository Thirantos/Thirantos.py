import secrets
from abc import ABC, abstractmethod
from time import time


class Authenticator(ABC):

    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def authenticate(self, password:str) -> str:
        pass

    @abstractmethod
    def use_token(self, token: str) -> bool:
        pass

    @abstractmethod
    def update_tokens(self) -> None:
        pass


class SinglePassAuth(Authenticator):
    def __init__(self, max_login_time: int, password: str):
        self.max_login_time = int(max_login_time)
        self.password = password
        self.tokens: dict[str, int] = {}

    def authenticate(self, password:str) -> str:
        token: str = ''
        if password == self.password:
            cur_time = int(time())
            token = secrets.token_urlsafe(32)
            self.tokens[token] = cur_time
        return token

    def use_token(self, token: str) -> bool:
        if token not in self.tokens:
            return False

        if time() - self.tokens[token] > self.max_login_time:
            self.tokens.pop(token)
            return False

        self.tokens[token] = int(time())
        return True

    def update_tokens(self) -> None:
        for t in self.tokens:
            if time() - self.tokens[t] > self.max_login_time:
                self.tokens.pop(t)