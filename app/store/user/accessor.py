from hashlib import sha256
import datetime

import sqlalchemy.exc
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

from app.base import BaseAccessor
from app.user.dataclasses import (
    UserDC,
    UserforRequest,
    AccessClassDC,
    UserAccessDC,
    UserAccessesDC,
    UserAccessInfoDC,
)
from app.user.models import UserModel, UserAccessModel, AccessClassModel


class UserAccessor(BaseAccessor):
    async def get_by_login(self, login: str) -> UserDC | None:
        async with self.app.database.session() as session:
            query = select(UserModel).where(UserModel.login == login)
            res = await session.scalars(query)
            user = res.one_or_none()
            if user:
                return UserDC(
                    id=user.id,
                    login=user.login,
                    name=user.name,
                    surname=user.surname,
                    password=user.password,
                )
            return None

    async def get_by_id(self, id: int) -> UserDC | None:
        async with self.app.database.session() as session:
            query = select(UserModel).where(UserModel.id == id)
            res = await session.scalars(query)
            user = res.one_or_none()
            if user:
                return UserDC(
                    id=user.id,
                    login=user.login,
                    name=user.name,
                    surname=user.surname,
                    password=user.password,
                )
            return None

    async def create_access(self, user_id: int, role_id: int) -> UserAccessDC | None:
        try:
            async with self.app.database.session() as session:
                useraccess = UserAccessModel(
                    user_id=user_id, access_id=role_id, date=datetime.datetime.utcnow()
                )
                session.add(useraccess)
                await session.commit()
                return useraccess.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None
        except sqlalchemy.exc.ProgrammingError:
            return None

    async def create_access_class(self, name: str) -> AccessClassDC | None:
        try:
            async with self.app.database.session() as session:
                access = AccessClassModel(name=name)
                session.add(access)
                await session.commit()
                return access.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None
        except sqlalchemy.exc.ProgrammingError:
            return None

    async def create_user(
        self, login: str, password: str, name: str, surname: str
    ) -> UserforRequest | None:
        try:
            async with self.app.database.session() as session:
                user = UserModel(
                    login=login,
                    password=sha256(password.encode()).hexdigest(),
                    name=name,
                    surname=surname,
                )
                session.add(user)
                await session.commit()
                await self.create_access(user.id, 1)
                return UserforRequest(
                    id=user.id,
                    login=user.login,
                    name=user.name,
                    surname=user.surname,
                )
        except sqlalchemy.exc.IntegrityError:
            return None
        except sqlalchemy.exc.ProgrammingError:
            return None

    async def remove_access(self, user_id: int, role_id: int) -> True | False:
        try:
            async with self.app.database.session() as session:
                query = delete(UserAccessModel).where(
                    (UserAccessModel.user_id == user_id)
                    & (UserAccessModel.access_id == role_id)
                )
                await session.execute(query)
                await session.commit()
                return True

        except sqlalchemy.exc.IntegrityError:
            return False
        except sqlalchemy.exc.ProgrammingError:
            return False

    async def get_user_accesses(self, user_id: int) -> UserAccessesDC | None:
        try:
            async with self.app.database.session() as session:
                user = await self.get_by_id(user_id)
                if user:
                    query = (
                        select(UserAccessModel)
                        .where(UserAccessModel.user_id == user_id)
                        .options(selectinload(UserAccessModel.accessgiven))
                    )
                    res = await session.scalars(query)
                    accesses = res.all()
                    return UserAccessesDC(
                        UserAccessInfoDC(
                            id=role.id,
                            access_id=AccessClassDC(
                                id=role.accessgiven.id, name=role.accessgiven.name
                            ),
                            user_id=role.user_id,
                            date=role.date,
                        )
                        for role in accesses
                    )
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None
        except sqlalchemy.exc.ProgrammingError:
            return None

    async def update_userinfo(
        self, user_id: int, name: str | None, surname: str | None
    ) -> UserforRequest | None:
        try:
            async with self.app.database.session() as session:
                if name or surname:
                    user = await self.get_by_id(user_id)
                    if name is None:
                        name = user.name
                    if surname is None:
                        surname = user.surname
                    query = (
                        update(UserModel)
                        .where(UserModel.user_id == user_id)
                        .values(name=name, surname=surname)
                    )
                    await session.execute(query)
                    await session.commit()
                    user = await self.get_by_id(user_id)
                    return user
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None
        except sqlalchemy.exc.ProgrammingError:
            return None

    async def get_role_by_id(self, id: int) -> AccessClassDC | None:
        async with self.app.database.session() as session:
            query = select(AccessClassModel).where(AccessClassModel.id == id)
            res = await session.scalars(query)
            role = res.one_or_none()
            if role:
                return role.to_dc()
            return None

    async def get_user_access(self, user_id: int, role_id: int) -> AccessClassDC | None:
        try:
            async with self.app.database.session() as session:
                query = select(UserAccessModel).where(
                    (UserAccessModel.user_id == user_id)
                    & (UserAccessModel.access_id == role_id)
                )
                res = await session.scalars(query)
                useraccess = res.one_or_none()
                if useraccess is None:
                    return None
                return useraccess.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None
        except sqlalchemy.exc.ProgrammingError:
            return None
