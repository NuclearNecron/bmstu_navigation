from aiohttp.web_exceptions import (
    HTTPForbidden,
    HTTPUnauthorized,
    HTTPBadRequest,
    HTTPConflict,
    HTTPNotFound,
)
from aiohttp_apispec import (
    request_schema,
)

from aiohttp_cors import CorsViewMixin
from aiohttp_session import new_session

from app.web.app import View
from app.web.mixin import AuthRequiredMixin
from app.web.utils import json_response

from app.user.schemas import (
    UserSchema,
    NewUserSchema,
    NewAccessSchema,
    NewUserAccessSchema,
    UpdUserSchema,
)
from app.user.dataclasses import KEY_TYPES


class UserLoginView(CorsViewMixin, View):
    @request_schema(UserSchema)
    async def post(self):
        logindata = await self.store.userAPI.get_by_login(self.data["login"])
        if logindata is None:
            raise HTTPForbidden
        user_data = {
            "id": logindata.id,
            "login": logindata.login,
            "name": logindata.name,
            "surname": logindata.surname,
        }
        if "password" in self.data and logindata.is_password_valid(self.data["password"]):
            session = await new_session(request=self.request)
            session["user"] = user_data
            return json_response(data=user_data)
        raise HTTPForbidden


class UserCurrentView(AuthRequiredMixin, CorsViewMixin, View):
    async def get(self):
        if self.request.user is not None:
            return json_response(
                data={
                    "id": self.request.user.id,
                    "login": self.request.user.login,
                    "name": self.request.user.name,
                    "surname": self.request.user.surname,
                }
            )
        raise HTTPUnauthorized


class UserCreate(CorsViewMixin, View):
    @request_schema(NewUserSchema)
    async def post(self):
        user = await self.store.userAPI.create_user(
            login=self.data["login"],
            password=self.data["password"],
            name=self.data["name"],
            surname=self.data["surname"],
        )
        if user is None:
            raise HTTPConflict
        return json_response(
            data={
                "id": user.id,
                "login": user.login,
                "name": user.name,
                "surname": user.surname,
            }
        )

    @request_schema(UpdUserSchema)
    async def put(self):
        if self.request.user is not None:
            user = await self.store.userAPI.update_userinfo(
                self.request.user.id,
                name=self.data.get("name"),
                surname=self.data.get("surname"),
            )
            if user is None:
                raise HTTPConflict
            return json_response(
                data={
                    "id": user.id,
                    "login": user.login,
                    "name": user.name,
                    "surname": user.surname,
                }
            )
        raise HTTPUnauthorized


class AccessView(AuthRequiredMixin, CorsViewMixin, View):
    @request_schema(NewAccessSchema)
    async def post(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        user = self.request.user
        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden
        roles = [access.access_id.name for access in acceses]
        if (KEY_TYPES.ADMIN in roles) or (KEY_TYPES.OWNER in roles):
            new_access = await self.store.userAPI.create_access_class(self.data["name"])
            if new_access is None:
                raise HTTPConflict
            return json_response(
                data={
                    "id": new_access.id,
                    "name": new_access.name,
                }
            )
        else:
            raise HTTPForbidden


class UserAccessView(AuthRequiredMixin, CorsViewMixin, View):
    async def get(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        user = self.request.user
        try:
            user_id = int(self.request.query["user_id"])
        except:
            acceses = await self.store.userAPI.get_user_accesses(user.id)
            return json_response(
                data={
                    "user": {"id": user.id, "name": user.name, "surname": user.surname},
                    "roles": [
                        {
                            "role": {
                                "id": access_role.access_id.id,
                                "name": access_role.access_id.name,
                            },
                            "date": access_role.date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        }
                        for access_role in acceses.roles
                    ],
                }
            )

        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden
        roles = [access.access_id.name for access in acceses.roles]
        if (KEY_TYPES.ADMIN in roles) or (KEY_TYPES.OWNER in roles):
            searched_user = await self.store.userAPI.get_by_id(user_id)
            if searched_user is None:
                raise HTTPNotFound
            acceses = await self.store.userAPI.get_user_accesses(searched_user.id)
            return json_response(
                data={
                    "user": {
                        "id": searched_user.id,
                        "name": searched_user.name,
                        "surname": searched_user.surname,
                    },
                    "roles": [
                        {
                            "role": {
                                "id": access_role.access_id.id,
                                "name": access_role.access_id.name,
                            },
                            "date": access_role.date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        }
                        for access_role in acceses.roles
                    ],
                }
            )
        else:
            raise HTTPForbidden

    @request_schema(NewUserAccessSchema)
    async def post(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        user = self.request.user
        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden
        roles = [access.access_id.name for access in acceses.roles]
        if (KEY_TYPES.ADMIN not in roles) and (KEY_TYPES.OWNER not in roles):
            raise HTTPForbidden
        search_user = await self.store.userAPI.get_by_id(self.data["user_id"])
        if search_user is None:
            raise HTTPBadRequest
        search_role = await self.store.userAPI.get_role_by_id(self.data["role_id"])
        if search_role is None:
            raise HTTPBadRequest
        if KEY_TYPES.OWNER not in roles:
            if (search_role.name == KEY_TYPES.OWNER) or (
                search_role.name == KEY_TYPES.ADMIN
            ):
                raise HTTPForbidden
            else:
                new_access = await self.store.userAPI.create_access(
                    search_user.id, search_role.id
                )
                if new_access is None:
                    raise HTTPBadRequest
                else:
                    return json_response(
                        data={
                            "id": new_access.id,
                            "access_id": new_access.access_id,
                            "user_id": new_access.user_id,
                            "date": new_access.date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        }
                    )
        else:
            new_access = await self.store.userAPI.create_access(
                search_user.id, search_role.id
            )
            if new_access is None:
                raise HTTPBadRequest
            else:
                return json_response(
                    data={
                        "id": new_access.id,
                        "access_id": new_access.access_id,
                        "user_id": new_access.user_id,
                        "date": new_access.date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    }
                )

    async def delete(self):
        if self.request.user is None:
            raise HTTPUnauthorized
        user = self.request.user
        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden
        roles = [access.access_id.name for access in acceses.roles]
        if (KEY_TYPES.ADMIN not in roles) and (KEY_TYPES.OWNER not in roles):
            raise HTTPForbidden
        try:
            user_id = int(self.request.query["user_id"])
        except:
            raise HTTPBadRequest
        try:
            role_id = int(self.request.query["role_id"])
        except:
            raise HTTPBadRequest
        search_user = await self.store.userAPI.get_by_id(user_id)
        if search_user is None:
            raise HTTPBadRequest
        search_role = await self.store.userAPI.get_role_by_id(role_id)
        if search_role is None:
            raise HTTPBadRequest
        selected_useracess = await self.store.userAPI.get_user_access(user_id, role_id)
        if selected_useracess is None:
            raise HTTPBadRequest
        if KEY_TYPES.OWNER not in roles:
            if (
                (search_role.name == KEY_TYPES.OWNER)
                or (search_role.name == KEY_TYPES.ADMIN)
                or (search_role.name == KEY_TYPES.USER)
            ):
                raise HTTPForbidden
            else:
                result = await self.store.userAPI.remove_access(user_id, role_id)
                if not result:
                    raise HTTPBadRequest
                else:
                    return json_response(data={"result": "Успешное удаление"})
        else:
            if (search_role.name == KEY_TYPES.OWNER) or (
                search_role.name == KEY_TYPES.USER
            ):
                raise HTTPForbidden
            else:
                result = await self.store.userAPI.remove_access(user_id, role_id)
                if not result:
                    raise HTTPBadRequest
                else:
                    return json_response(data={"result": "Успешное удаление"})
