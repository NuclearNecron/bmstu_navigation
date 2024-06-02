from aiohttp.web_exceptions import (
    HTTPForbidden,
    HTTPUnauthorized,
    HTTPBadRequest,
    HTTPNotFound,
    HTTPServiceUnavailable
)
from aiohttp_apispec import (
    request_schema,
)

from aiohttp_cors import CorsViewMixin
from app.web.app import View
from app.web.utils import json_response

from app.map.schemas import (
    NewConnSchema,
    NewNodeSchema,
    NewTypeSchema,
    UpdConnSchema,
    UpdNodeSchema,
    UpdTypeSchema,
)
from app.user.dataclasses import KEY_TYPES


class NavigateView(CorsViewMixin, View):
    async def get(self):
        if not self.store.map.working:
            raise HTTPServiceUnavailable(reason="Модуль навигации еще не запущен. Запустите навигатор и попробуйте снова.")
        try:
            start_id = int(self.request.query.get("start_id"))
            target_id = int(self.request.query.get("target_id"))
        except:
            raise HTTPBadRequest(resaon="Не указаны необходимые параметры") 
        if not start_id or not target_id:
            raise HTTPBadRequest(resaon="Не указаны необходимые параметры")
        start_node = await self.store.mapAPI.get_node_by_id(start_id)
        target_node = await self.store.mapAPI.get_node_by_id(target_id)
        if (start_node is None) or (target_node is None):
            raise HTTPNotFound(resaon="Не существует указанной зоны")
        route = await self.store.map.navigate_main(start_id, target_id)
        return json_response(
            data={
                "route": [
                    {"id": route_node.id, "name": route_node.name} for route_node in route
                ]
            }
        )


class StartView(CorsViewMixin, View):
    async def post(self):
        if not self.store.map.working:
            await self.store.map.start()
            return json_response(data={"result": "Система навигации запущена успешно"})
        else:
            return json_response(data={"result": "Система навигации уже запущена"})


class TypeView(CorsViewMixin, View):
    async def get(self):
        try:
            type_id = int(self.request.rel_url.name)
        except:
            page = int(self.request.query.get("page", 1))
            if page < 1:
                raise HTTPBadRequest(resaon="Неверный параметр")
            unlimited = int(self.request.query.get("unlimited", 0))
            if unlimited == 1:
                types = await self.store.mapAPI.get_all_types(page=None,limit=None)
            else:
                types = await self.store.mapAPI.get_all_types(page=page, limit=10)
            if not types:
                raise HTTPNotFound(resaon="Вы вышли за границы списка")
            return json_response(
                data=[
                    {
                        "id": nodetype.id,
                        "parent_id": nodetype.parent_id,
                        "name": nodetype.name,
                        "shortname": nodetype.shortname,
                        "description": nodetype.description,
                    }
                    for nodetype in types.types
                ]
            )
        search_type = await self.store.mapAPI.get_type_by_id(type_id)
        if search_type is None:
            raise HTTPNotFound(resaon="Не существует")
        return json_response(
            data={
                "id": search_type.id,
                "parent_id": search_type.parent_id,
                "name": search_type.name,
                "shortname": search_type.shortname,
                "description": search_type.description,
            }
        )

    @request_schema(NewTypeSchema)
    async def post(self):
        if self.request.user is None:
            raise HTTPUnauthorized(resaon="Нет авторизации")
        user = self.request.user
        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        roles = [access.access_id.name for access in acceses.roles]
        if (KEY_TYPES.ADMIN not in roles) and (KEY_TYPES.OWNER not in roles):
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        new_type = await self.store.mapAPI.createType(
            name=self.data["name"],
            shortname=self.data["shortname"],
            parent_id=self.data.get("parent_id"),
            description=self.data.get("description"),
        )
        if new_type is None:
            raise HTTPBadRequest(resaon="Ошибка при создании")
        if self.store.map.working:
            await self.store.map.add_type(new_type)
        return json_response(
            data={
                "id": new_type.id,
                "parent_id": new_type.parent_id,
                "name": new_type.name,
                "shortname": new_type.shortname,
                "description": new_type.description,
            }
        )

    @request_schema(UpdTypeSchema)
    async def put(self):
        if self.request.user is None:
            raise HTTPUnauthorized(resaon="Вы не авторизованы")
        user = self.request.user
        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        roles = [access.access_id.name for access in acceses.roles]
        if (KEY_TYPES.ADMIN not in roles) and (KEY_TYPES.OWNER not in roles):
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        try:
            type_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest(resaon="Не указан тип")
        search_type = await self.store.mapAPI.get_type_by_id(type_id)
        if search_type is None:
            raise HTTPNotFound(resaon="Нет такого типа")
        if self.data.get("name"):
            search_type.name = self.data.get("name")
        if self.data.get("description"):
            search_type.description = self.data.get("description")
        if self.data.get("shortname"):
            search_type.shortname = self.data.get("shortname")
        upd_type = await self.store.mapAPI.update_typeinfo(
            type_id,
            name=search_type.name,
            shortname=search_type.shortname,
            description=search_type.description,
        )
        if upd_type is None:
            raise HTTPBadRequest("Ошибка при изменении")
        if self.store.map.working:
            await self.store.map.change_type(upd_type)
        return json_response(
            data={
                "id": upd_type.id,
                "parent_id": upd_type.parent_id,
                "name": upd_type.name,
                "shortname": upd_type.shortname,
                "description": upd_type.description,
            }
        )

    async def delete(self):
        if self.request.user is None:
            raise HTTPUnauthorized(resaon="Вы не авторизованы")
        user = self.request.user
        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        roles = [access.access_id.name for access in acceses.roles]
        if (KEY_TYPES.ADMIN not in roles) and (KEY_TYPES.OWNER not in roles):
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        try:
            type_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest(resaon="Нет указан ресурс")
        search_type = await self.store.mapAPI.get_type_by_id(type_id)
        if search_type is None:
            raise HTTPNotFound(resaon="Указанный ресурс не существует")
        result = await self.store.mapAPI.deleteType(type_id)
        if not result:
            raise HTTPBadRequest(resaon="Ошибка при удалении")
        if self.store.map.working:
            await self.store.map.delete_type(type_id)
        return json_response(data={"result": "Успешное удаление"})


class NodeView(CorsViewMixin, View):
    async def get(self):
        try:
            node_id = int(self.request.rel_url.name)
        except:
            page = int(self.request.query.get("page", 1))
            if page < 1:
                raise HTTPBadRequest(resaon="Неправильный парметр")
            node_type = int(self.request.query.get("type", 0))
            if node_type < 0:
                raise HTTPBadRequest(resaon="Неправильный параметр")
            unlimited = int(self.request.query.get("unlimited", 0))
            parent = int(self.request.query.get("parent_node", 0))
            if parent < 0:
                raise HTTPBadRequest(resaon="Неправлиьный параметр")
            if unlimited == 1:
                nodes = await self.store.mapAPI.get_all_nodes(page=None,limit=None)
            elif node_type:
                nodes = await self.store.mapAPI.get_all_children_of_type(node_type)
            elif parent:
                nodes = await self.store.mapAPI.get_all_children_nodes_of_node(parent)
            else:
                nodes = await self.store.mapAPI.get_all_nodes(page=page, limit=10)
            if not nodes:
                raise HTTPNotFound(resaon="Вы вышли за пределы списка зон")
            try:
                user = self.request.user
                acceses = await self.store.userAPI.get_user_accesses(user.id)
                roles = [access.access_id.name for access in acceses.roles]
                if (
                    (KEY_TYPES.ADMIN in roles)
                    or (KEY_TYPES.OWNER in roles)
                    or (KEY_TYPES.EDITOR in roles)
                ):
                    return json_response(
                        data={
                            "nodes": [
                                {
                                    "id": node.id,
                                    "parent_id": node.parent_id,
                                    "creator_id": node.creator_id,
                                    "created_time": node.created_time.strftime(
                                        "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ),
                                    "editor_id": node.editor_id,
                                    "edited_time": node.edited_time.strftime(
                                        "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ),
                                    "type": node.type_id,
                                    "name": node.name,
                                    "shortname": node.shortname,
                                    "description": node.description,
                                    "x_cord": node.x_cord,
                                    "y_cord": node.y_cord,
                                    "z_cord": node.z_cord,
                                }
                                for node in nodes.nodes
                            ]
                        }
                    )
            except:
                return json_response(
                data={
                    "nodes": [
                        {
                            "id": node.id,
                            "parent_id": node.parent_id,
                            "type": node.type_id,
                            "name": node.name,
                            "shortname": node.shortname,
                            "description": node.description,
                        }
                        for node in nodes.nodes
                    ]
                }
            )
        target_node = await self.store.mapAPI.get_node_by_id(node_id)
        if target_node is None:
            raise HTTPNotFound(resaon="Не существует запрашиваемого ресурса")
        node_type = await self.store.mapAPI.get_type_by_id(target_node.type_id)
        if self.request.user:
            user = self.request.user
            acceses = await self.store.userAPI.get_user_accesses(user.id)
            roles = [access.access_id.name for access in acceses.roles]
            if (
                (KEY_TYPES.ADMIN in roles)
                or (KEY_TYPES.OWNER in roles)
                or (KEY_TYPES.EDITOR in roles)
            ):
                return json_response(
                    data={
                        "id": target_node.id,
                        "parent_id": target_node.parent_id,
                        "creator_id": target_node.creator_id,
                        "created_time": target_node.created_time.strftime(
                                        "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ),
                        "editor_id": target_node.editor_id,
                        "edited_time": target_node.edited_time.strftime(
                                        "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ),
                        "type": {
                            "id": node_type.id,
                            "name": node_type.name,
                            "shortname": node_type.shortname,
                            "description": node_type.description,
                        },
                        "name": target_node.name,
                        "shortname": target_node.shortname,
                        "description": target_node.description,
                        "x_cord": target_node.x_cord,
                        "y_cord": target_node.y_cord,
                        "z_cord": target_node.z_cord,
                    }
                )
        return json_response(
            data={
                "id": target_node.id,
                "parent_id": target_node.parent_id,
                "type": {
                    "id": node_type.id,
                    "name": node_type.name,
                    "shortname": node_type.shortname,
                    "description": node_type.description,
                },
                "name": target_node.name,
                "shortname": target_node.shortname,
                "description": target_node.description,
            }
        )

    @request_schema(NewNodeSchema)
    async def post(self):
        if self.request.user is None:
            raise HTTPUnauthorized(resaon="Вы не авторизованы")
        user = self.request.user
        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden(resaon="Дотсуп к ресурсу запрещен")
        roles = [access.access_id.name for access in acceses.roles]
        if (KEY_TYPES.ADMIN not in roles) and (KEY_TYPES.OWNER not in roles):
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        new_node = await self.store.mapAPI.createNode(
            name=self.data["name"],
            shortname=self.data["shortname"],
            parent_id=self.data.get("parent_id"),
            description=self.data.get("description"),
            user_id=user.id,
            type_id=self.data["type_id"],
            x_cord=self.data["x"],
            y_cord=self.data["y"],
            z_cord=self.data["z"],
        )
        if new_node is None:
            raise HTTPBadRequest(resaon="Ошибка при создании")
        if self.store.map.working:
            await self.store.map.add_node(new_node)
        return json_response(
            data={
                "id": new_node.id,
                "name": new_node.name,
                "shortname": new_node.shortname,
                "parent_id": new_node.parent_id,
                "creator_id": new_node.creator_id,
                "editor_id": new_node.editor_id,
                "created_time": new_node.created_time.strftime(
                                        "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ),
                "edited_time": new_node.edited_time.strftime(
                                        "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ),
                "type_id": new_node.type_id,
                "description": new_node.description,
                "x_cord": new_node.x_cord,
                "y_cord": new_node.y_cord,
                "z_cord": new_node.z_cord,
            }
        )

    @request_schema(UpdNodeSchema)
    async def put(self):
        if self.request.user is None:
            raise HTTPUnauthorized(resaon="Вы не авторизованы")
        user = self.request.user
        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        roles = [access.access_id.name for access in acceses.roles]
        if (
            (KEY_TYPES.ADMIN not in roles)
            and (KEY_TYPES.OWNER not in roles)
            and (KEY_TYPES.EDITOR not in roles)
        ):
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        try:
            node_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest(resaon="Не указан запрашиваеемый ресурс")
        old_node = await self.store.mapAPI.get_node_by_id(node_id)
        if old_node is None:
            raise HTTPNotFound(resaon="Запрашиваемый ресурс не существует")
        if self.data.get("name"):
            old_node.name = self.data.get("name")
        if self.data.get("description"):
            old_node.description = self.data.get("description")
        if self.data.get("shortname"):
            old_node.shortname = self.data.get("shortname")
        if self.data.get("x"):
            old_node.x_cord = self.data.get("x")
        if self.data.get("y"):
            old_node.y_cord = self.data.get("y")
        if self.data.get("z"):
            old_node.z_cord = self.data.get("z")
        upd_node = await self.store.mapAPI.update_nodeinfo(
            id=node_id,
            user_id=user.id,
            name=old_node.name,
            shortname=old_node.shortname,
            description=old_node.description,
            x_cord=old_node.x_cord,
            y_cord=old_node.y_cord,
            z_cord=old_node.z_cord,
        )
        if upd_node is None:
            raise HTTPBadRequest(resaon="Ошибка при обновлении")
        if self.store.map.working:
            await self.store.map.change_node(upd_node)
        return json_response(
            data={
                "id": upd_node.id,
                "name": upd_node.name,
                "shortname": upd_node.shortname,
                "parent_id": upd_node.parent_id,
                "creator_id": upd_node.creator_id,
                "editor_id": upd_node.editor_id,
                "created_time": upd_node.created_time.strftime(
                                        "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ),
                "edited_time": upd_node.edited_time.strftime(
                                        "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ),
                "type_id": upd_node.type_id,
                "description": upd_node.description,
                "x_cord": upd_node.x_cord,
                "y_cord": upd_node.y_cord,
                "z_cord": upd_node.z_cord,
            }
        )

    async def delete(self):
        if self.request.user is None:
            raise HTTPUnauthorized(resaon="Вы не авторизованы")
        user = self.request.user
        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        roles = [access.access_id.name for access in acceses.roles]
        if (KEY_TYPES.ADMIN not in roles) and (KEY_TYPES.OWNER not in roles):
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        try:
            node_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest(resaon="Запрашиваемый ресурс не указан")
        search_node = await self.store.mapAPI.get_node_by_id(node_id)
        if search_node is None:
            raise HTTPNotFound(resaon="Запрашиваемый ресурс не существует")
        result = await self.store.mapAPI.deleteNode(node_id)
        if not result:
            raise HTTPBadRequest(resaon="Ошибка при удалении")
        if self.store.map.working:
            await self.store.map.delete_node(node_id)
        return json_response(data={"result": "Успешное удаление"})


class ConnectionView(CorsViewMixin, View):
    async def get(self):
        try:
            conn_id = int(self.request.rel_url.name)
        except:
            page = int(self.request.query.get("page", 1))
            if page < 1:
                raise HTTPBadRequest(resaon="Неверный параметр")
            node = int(self.request.query.get("node", 0))
            if node < 0:
                raise HTTPBadRequest(resaon="Неверный параметр")
            unlimited = int(self.request.query.get("unlimited", 0))
            if unlimited == 1:
                conns = await self.store.mapAPI.get_all_connections(page=None,limit=None)
            elif node:
                conns = await self.store.mapAPI.get_all_connections_of_node(node)
            else:
                conns = await self.store.mapAPI.get_all_connections(page=page, limit=10)
            if not conns:
                raise HTTPNotFound(resaon="Вы вышли за пределы списка соединений")
            return json_response(
                data={
                    "connections": [
                        {
                            "id": conn.id,
                            "node1_id": conn.node1_id,
                            "node2_id": conn.node2_id,
                            "distance": conn.distance,
                            "time": conn.time,
                            "t_weight": conn.t_weight,
                        }
                        for conn in conns.conns
                    ]
                }
            )
        target_conn = await self.store.mapAPI.get_connection_by_id(conn_id)
        if target_conn is None:
            raise HTTPNotFound(resaon="Запрашиваемый ресурс не существует")
        node1 = await self.store.mapAPI.get_node_by_id(target_conn.node1_id)
        node2 = await self.store.mapAPI.get_node_by_id(target_conn.node2_id)
        if self.request.user:
            user = self.request.user
            acceses = await self.store.userAPI.get_user_accesses(user.id)
            roles = [access.access_id.name for access in acceses.roles]
            if (
                (KEY_TYPES.ADMIN in roles)
                or (KEY_TYPES.OWNER in roles)
                or (KEY_TYPES.EDITOR in roles)
            ):
                return json_response(
                    data={
                        "id": target_conn.id,
                        "node1": {
                            "id": node1.id,
                            "parent_id": node1.parent_id,
                            "creator_id": node1.creator_id,
                            "created_time": node1.created_time.strftime(
                                        "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ),
                            "editor_id": node1.editor_id,
                            "edited_time": node1.edited_time.strftime(
                                        "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ),
                            "type_id": node1.type_id,
                            "name": node1.name,
                            "shortname": node1.shortname,
                            "description": node1.description,
                            "x_cord": node1.x_cord,
                            "y_cord": node1.y_cord,
                            "z_cord": node1.z_cord,
                        },
                        "node2": {
                            "id": node2.id,
                            "parent_id": node2.parent_id,
                            "creator_id": node2.creator_id,
                            "created_time": node2.created_time.strftime(
                                        "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ),
                            "editor_id": node2.editor_id,
                            "edited_time": node2.edited_time.strftime(
                                        "%Y-%m-%dT%H:%M:%S.%fZ"
                                    ),
                            "type": node2.type_id,
                            "name": node2.name,
                            "shortname": node2.shortname,
                            "description": node2.description,
                            "x_cord": node2.x_cord,
                            "y_cord": node2.y_cord,
                            "z_cord": node2.z_cord,
                        },
                        "distance": target_conn.distance,
                        "time": target_conn.time,
                        "t_weight": target_conn.t_weight,
                    }
                )
        return json_response(
            data={
                "id": target_conn.id,
                "node1": {
                    "id": node1.id,
                    "parent_id": node1.parent_id,
                    "type_id": node1.type_id,
                    "name": node1.name,
                    "shortname": node1.shortname,
                    "description": node1.description,
                },
                "node2": {
                    "id": node2.id,
                    "parent_id": node2.parent_id,
                    "type": node2.type_id,
                    "name": node2.name,
                    "shortname": node2.shortname,
                    "description": node2.description,
                },
                "distance": target_conn.distance,
                "time": target_conn.time,
                "t_weight": target_conn.t_weight,
            }
        )

    @request_schema(NewConnSchema)
    async def post(self):
        if self.request.user is None:
            raise HTTPUnauthorized(resaon="Вы не авторизованы")
        user = self.request.user
        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden(resaon="Доступ к запрашиваемому ресурсу запрещен")
        roles = [access.access_id.name for access in acceses.roles]
        if (KEY_TYPES.ADMIN not in roles) and (KEY_TYPES.OWNER not in roles):
            raise HTTPForbidden(resaon="Доступ к запрашиваемому ресурсу запрещен")
        if self.data["node1_id"] == self.data["node2_id"]:
            raise HTTPBadRequest(resaon='''Соединение на "само себя" ''')
        new_conn = await self.store.mapAPI.createConnection(
            node1_id=self.data["node1_id"],
            node2_id=self.data["node2_id"],
            distance=self.data["distance"],
            time=self.data["time"],
            t_weight=self.data["t_weight"],
        )
        if new_conn is None:
            raise HTTPBadRequest(resaon="Ошибка при создании")
        if self.store.map.working:
            await self.store.map.add_conn(new_conn)
        return json_response(
            data={
                "id":new_conn.id,
                "node1_id": new_conn.node1_id,
                "node2_id": new_conn.node2_id,
                "distance": new_conn.distance,
                "time": new_conn.time,
                "t_weight": new_conn.t_weight,
            }
        )

    @request_schema(UpdConnSchema)
    async def put(self):
        if self.request.user is None:
            raise HTTPUnauthorized(resaon="Вы не авторизованы")
        user = self.request.user
        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        roles = [access.access_id.name for access in acceses.roles]
        if (
            (KEY_TYPES.ADMIN not in roles)
            and (KEY_TYPES.OWNER not in roles)
            and (KEY_TYPES.EDITOR not in roles)
        ):
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        try:
            conn_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest(resaon="Не указан запршиваемый ресурс")
        old_conn = await self.store.mapAPI.get_connection_by_id(conn_id)
        if old_conn is None:
            raise HTTPNotFound(resaon="Запрашиваемый ресурс не существует")
        if self.data.get("distance"):
            old_conn.distance = self.data.get("distance")
        if self.data.get("t_weight"):
            old_conn.t_weight = self.data.get("t_weight")
        if self.data.get("time"):
            old_conn.time = self.data.get("time")
        upd_conn = await self.store.mapAPI.update_conninfo(
            id=conn_id,
            distance=old_conn.distance,
            time=old_conn.time,
            t_weight=old_conn.t_weight,
        )
        if upd_conn is None:
            raise HTTPBadRequest(resaon="Ошибка при изменении")
        if self.store.map.working:
            await self.store.map.change_conn(upd_conn)
        return json_response(
            data={
                "id":upd_conn.id,
                "node1_id": upd_conn.node1_id,
                "node2_id": upd_conn.node2_id,
                "distance": upd_conn.distance,
                "time": upd_conn.time,
                "t_weight": upd_conn.t_weight,
            }
        )

    async def delete(self):
        if self.request.user is None:
            raise HTTPUnauthorized(resaon="Вы не авторизованы")
        user = self.request.user
        acceses = await self.store.userAPI.get_user_accesses(user.id)
        if acceses is None:
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        roles = [access.access_id.name for access in acceses.roles]
        if (KEY_TYPES.ADMIN not in roles) and (KEY_TYPES.OWNER not in roles):
            raise HTTPForbidden(resaon="Доступ к ресурсу запрещен")
        try:
            conn_id = int(self.request.rel_url.name)
        except:
            raise HTTPBadRequest(resaon="Не указан запрашиваемый ресурс")
        seacrh_conn = await self.store.mapAPI.get_connection_by_id(conn_id)
        if seacrh_conn is None:
            raise HTTPNotFound(resaon="Запрашиваемый ресурс не существует")
        result = await self.store.mapAPI.deleteConnection(conn_id)
        if not result:
            raise HTTPBadRequest(resaon="Ошибка при удалении")
        if self.store.map.working:
            await self.store.map.delete_conn(conn_id,seacrh_conn.node1_id,seacrh_conn.node2_id)
        return json_response(data={"result": "Успешное удаление"})
