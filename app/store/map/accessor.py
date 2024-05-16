import datetime
import sqlalchemy.exc
from sqlalchemy import select, delete, update, or_

from app.base import BaseAccessor
from app.map.dataclasses import (
    NodeDC,
    NodeConnectionDC,
    NodetypeDC,
    ConnectionsDC,
    TypesDC,
    NodesDC,
)

from app.map.models import NodeModel, TypeModel, ConnectionModel


class MapAccessor(BaseAccessor):
    async def createType(
        self, name: str, shortname: str, parent_id: int | None, description: str | None
    ) -> NodetypeDC | None:
        try:
            async with self.app.database.session() as session:
                nodeType = TypeModel(
                    name=name,
                    shortname=shortname,
                    parent_id=parent_id,
                    description=description,
                )
                session.add(nodeType)
                await session.commit()
                return nodeType.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None
        except sqlalchemy.exc.ProgrammingError:
            return None

    async def createNode(
        self,
        name: str,
        shortname: str,
        parent_id: int | None,
        user_id: int,
        type_id: int,
        description: str | None,
        x_cord: float,
        y_cord: float,
        z_cord: float,
    ) -> NodeDC | None:
        try:
            async with self.app.database.session() as session:
                node = NodeModel(
                    name=name,
                    shortname=shortname,
                    parent_id=parent_id,
                    description=description,
                    creator_id=user_id,
                    editor_id=user_id,
                    type_id=type_id,
                    x_cord=x_cord,
                    y_cord=y_cord,
                    z_cord=z_cord,
                    created_time=datetime.datetime.utcnow(),
                    edited_time=datetime.datetime.utcnow(),
                )
                session.add(node)
                await session.commit()
                return node.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None
        except sqlalchemy.exc.ProgrammingError:
            return None

    async def createConnection(
        self, node1_id: int, node2_id: int, distance: float, time: float, t_weight: float
    ) -> NodeConnectionDC | None:
        try:
            async with self.app.database.session() as session:
                connection = ConnectionModel(
                    node1_id=node1_id,
                    node2_id=node2_id,
                    distance=distance,
                    time=time,
                    t_weight=t_weight,
                )
                session.add(connection)
                await session.commit()
                return connection.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None
        except sqlalchemy.exc.ProgrammingError:
            return None

    async def deleteNode(self, id: int) -> False | True:
        try:
            async with self.app.database.session() as session:
                query = delete(NodeModel).where(NodeModel.id == id)
                await session.execute(query)
                await session.commit()
                return True
        except sqlalchemy.exc.IntegrityError:
            return False
        except sqlalchemy.exc.ProgrammingError:
            return False

    async def deleteType(self, id: int) -> False | True:
        try:
            async with self.app.database.session() as session:
                query = delete(TypeModel).where(TypeModel.id == id)
                await session.execute(query)
                await session.commit()
                return True
        except sqlalchemy.exc.IntegrityError:
            return False
        except sqlalchemy.exc.ProgrammingError:
            return False

    async def deleteConnection(self, id: int) -> False | True:
        try:
            async with self.app.database.session() as session:
                query = delete(ConnectionModel).where(ConnectionModel.id == id)
                await session.execute(query)
                await session.commit()
                return True
        except sqlalchemy.exc.IntegrityError:
            return False
        except sqlalchemy.exc.ProgrammingError:
            return False

    async def get_node_by_id(self, id: int) -> NodeDC | None:
        async with self.app.database.session() as session:
            query = select(NodeModel).where(NodeModel.id == id)
            res = await session.scalars(query)
            node = res.one_or_none()
            if node:
                return NodeDC(
                    id=node.id,
                    parent_id=node.parent_id,
                    creator_id=node.creator_id,
                    edited_time=node.edited_time,
                    editor_id=node.editor_id,
                    created_time=node.created_time,
                    type_id=node.type_id,
                    name=node.name,
                    shortname=node.shortname,
                    description=node.description,
                    x_cord=node.x_cord,
                    y_cord=node.y_cord,
                    z_cord=node.z_cord,
                )
            return None

    async def get_type_by_id(self, id: int) -> NodetypeDC | None:
        async with self.app.database.session() as session:
            query = select(TypeModel).where(TypeModel.id == id)
            res = await session.scalars(query)
            nodeType = res.one_or_none()
            if nodeType:
                return NodetypeDC(
                    id=nodeType.id,
                    parent_id=nodeType.parent_id,
                    name=nodeType.name,
                    shortname=nodeType.shortname,
                    description=nodeType.description,
                )
            return None

    async def get_connection_by_id(self, id: int) -> NodeConnectionDC | None:
        async with self.app.database.session() as session:
            query = select(ConnectionModel).where(ConnectionModel.id == id)
            res = await session.scalars(query)
            conn = res.one_or_none()
            if conn:
                return NodeConnectionDC(
                    id=conn.id,
                    node1_id=conn.node1_id,
                    node2_id=conn.node2_id,
                    distance=conn.distance,
                    time=conn.time,
                    t_weight=conn.t_weight,
                )
            return None

    async def update_nodeinfo(
        self,
        id: int,
        user_id: int,
        name: str,
        shortname: str,
        description: str | None,
        x_cord: float,
        y_cord: float,
        z_cord: float,
    ) -> NodeDC | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    update(NodeModel)
                    .where(NodeModel.id == id)
                    .values(
                        name=name,
                        shortname=shortname,
                        description=description,
                        x_cord=x_cord,
                        y_cord=y_cord,
                        z_cord=z_cord,
                        editor_id=user_id,
                        edited_time=datetime.datetime.utcnow(),
                    )
                )
                await session.execute(query)
                await session.commit()
                node = await self.get_node_by_id(id)
                return node
        except sqlalchemy.exc.IntegrityError:
            return None
        except sqlalchemy.exc.ProgrammingError:
            return None

    async def update_typeinfo(
        self, id: int, name: str, shortname: str, description: str | None
    ) -> NodetypeDC | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    update(TypeModel)
                    .where(TypeModel.id == id)
                    .values(
                        name=name,
                        shortname=shortname,
                        description=description,
                    )
                )
                await session.execute(query)
                await session.commit()
                nodeType = await self.get_type_by_id(id)
                return nodeType
        except sqlalchemy.exc.IntegrityError:
            return None
        except sqlalchemy.exc.ProgrammingError:
            return None

    async def update_conninfo(
        self, id: int, distance: float, time: float, t_weight: float
    ) -> NodeConnectionDC | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    update(ConnectionModel)
                    .where(ConnectionModel.id == id)
                    .values(distance=distance, time=time, t_weight=t_weight)
                )
                await session.execute(query)
                await session.commit()
                conn = await self.get_connection_by_id(id)
                return conn
        except sqlalchemy.exc.IntegrityError:
            return None
        except sqlalchemy.exc.ProgrammingError:
            return None

    async def get_all_nodes(self, page: int | None, limit: int | None) -> NodesDC | None:
        try:
            async with self.app.database.session() as session:
                if page and limit:
                    query = select(NodeModel).limit(limit).offset((page - 1) * limit).order_by(NodeModel.id)
                else:
                    query = select(NodeModel).order_by(NodeModel.id)
                res = await session.scalars(query)
                results = res.all()
                if results:
                    return NodesDC(
                        nodes=[
                            NodeDC(
                                id=node.id,
                                parent_id=node.parent_id,
                                creator_id=node.creator_id,
                                edited_time=node.edited_time,
                                editor_id=node.editor_id,
                                created_time=node.created_time,
                                type_id=node.type_id,
                                name=node.name,
                                shortname=node.shortname,
                                description=node.description,
                                x_cord=node.x_cord,
                                y_cord=node.y_cord,
                                z_cord=node.z_cord,
                            )
                            for node in results
                        ]
                    )
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_all_types(self, page: int | None, limit: int | None) -> TypesDC | None:
        try:
            async with self.app.database.session() as session:
                if page and limit:
                    query = select(TypeModel).limit(limit).offset((page - 1) * limit).order_by(TypeModel.id)
                else:
                    query = select(TypeModel).order_by(TypeModel.id)
                res = await session.scalars(query)
                results = res.all()
                if results:
                    return TypesDC(
                        types=[
                            NodetypeDC(
                                id=nodeType.id,
                                parent_id=nodeType.parent_id,
                                name=nodeType.name,
                                shortname=nodeType.shortname,
                                description=nodeType.description,
                            )
                            for nodeType in results
                        ]
                    )
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_all_connections(
        self, page: int | None, limit: int | None
    ) -> ConnectionsDC | None:
        try:
            async with self.app.database.session() as session:
                if page and limit:
                    query = (
                        select(ConnectionModel)
                        .limit(limit)
                        .offset((page - 1) * limit).order_by(ConnectionModel.id)
                    )
                else:
                    query = select(ConnectionModel).order_by(ConnectionModel.id)
                res = await session.scalars(query)
                results = res.all()
                if results:
                    return ConnectionsDC(
                        conns=[
                            NodeConnectionDC(
                                id=conn.id,
                                node1_id=conn.node1_id,
                                node2_id=conn.node2_id,
                                distance=conn.distance,
                                time=conn.time,
                                t_weight=conn.t_weight,
                            )
                            for conn in results
                        ]
                    )
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_all_connections_of_node(self, node_id: int) -> ConnectionsDC | None:
        try:
            async with self.app.database.session() as session:
                query = select(ConnectionModel).where(
                    or_(
                        ConnectionModel.node1_id == node_id,
                        ConnectionModel.node2_id == node_id,
                    )
                ).order_by(ConnectionModel.id)
                res = await session.scalars(query)
                results = res.all()
                if results:
                    return ConnectionsDC(
                        conns=[
                            NodeConnectionDC(
                                id=conn.id,
                                node1_id=conn.node1_id,
                                node2_id=conn.node2_id,
                                distance=conn.distance,
                                time=conn.time,
                                t_weight=conn.t_weight,
                            )
                            for conn in results
                        ]
                    )
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_all_children_nodes_of_node(self, node_id: int) -> NodesDC | None:
        try:
            async with self.app.database.session() as session:
                query = select(NodeModel).where(NodeModel.parent_id == node_id).order_by(NodeModel.id)
                res = await session.scalars(query)
                results = res.all()
                if results:
                    return NodesDC(
                        nodes=[
                            NodeDC(
                                id=node.id,
                                parent_id=node.parent_id,
                                creator_id=node.creator_id,
                                edited_time=node.edited_time,
                                editor_id=node.editor_id,
                                created_time=node.created_time,
                                type_id=node.type_id,
                                name=node.name,
                                shortname=node.shortname,
                                description=node.description,
                                x_cord=node.x_cord,
                                y_cord=node.y_cord,
                                z_cord=node.z_cord,
                            )
                            for node in results
                        ]
                    )
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_all_children_of_type(self, type_id: int) -> NodesDC | None:
        try:
            async with self.app.database.session() as session:
                query = select(NodeModel).where(NodeModel.type_id == type_id).order_by(NodeModel.id)
                res = await session.scalars(query)
                results = res.all()
                if results:
                    return NodesDC(
                        nodes=[
                            NodeDC(
                                id=node.id,
                                parent_id=node.parent_id,
                                creator_id=node.creator_id,
                                edited_time=node.edited_time,
                                editor_id=node.editor_id,
                                created_time=node.created_time,
                                type_id=node.type_id,
                                name=node.name,
                                shortname=node.shortname,
                                description=node.description,
                                x_cord=node.x_cord,
                                y_cord=node.y_cord,
                                z_cord=node.z_cord,
                            )
                            for node in results
                        ]
                    )
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None
