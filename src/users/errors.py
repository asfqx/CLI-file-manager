from dataclasses import dataclass


@dataclass
class UserNotFoundError(Exception):
    detail: str = "User not found"


@dataclass
class InvalidPasswordError(Exception):
    detail: str = "Login or password is incorrect"
