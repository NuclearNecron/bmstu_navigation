from dataclasses import dataclass
from hashlib import sha256
import datetime

from aiohttp_session import Session


@dataclass
class UserforRequest:
    id: int
    login: str
    name: str
    surname: str


@dataclass
class UserDC:
    id: int
    login: str
    name: str
    surname: str
    password: str

    def is_password_valid(self, password: str) -> bool:
        return self.password == sha256(password.encode()).hexdigest()

    @staticmethod
    def from_session(session: Session | None) -> UserforRequest | None:
        if session and session["user"]:
            return UserforRequest(
                id=session["user"]["id"],
                login=session["user"]["login"],
                name=session["user"]["name"],
                surname=session["user"]["surname"],
            )
        return None


@dataclass
class AccessClassDC:
    id: int
    name: str


@dataclass
class UserAccessDC:
    id: int
    access_id: int
    user_id: int
    date: datetime


@dataclass
class UserAccessInfoDC:
    id: int
    access_id: AccessClassDC
    user_id: int
    date: datetime


@dataclass
class UserAccessesDC:
    roles: list[UserAccessInfoDC]


class KEY_TYPES:
    OWNER = "Владелец"
    ADMIN = "Администратор"
    EDITOR = "Редактор"
    USER = "Пользователь"
