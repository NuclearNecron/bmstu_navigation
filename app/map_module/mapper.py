import typing
import gc
import math
import heapq
from app.map_module.node import NodeType, Node, Connection, RouteNode
from app.map_module.dataclasses import KEY_TYPES
from app.map.dataclasses import NodetypeDC, NodeDC, NodeConnectionDC


if typing.TYPE_CHECKING:
    from app.web.app import Application


class Map:

    def __init__(self, app: "Application"):
        self.app = app
        self.types = dict()
        self.nodes = dict()
        self.all_cones = dict()
        self.exits = dict()
        self.exits_list = set()
        self.working = False

    async def start(self):
        nodetypes = await self.app.store.mapAPI.get_all_types(page=None, limit=None)
        for nodetype in nodetypes.types:
            if nodetype.parent_id:
                self.types[f"{nodetype.id}"] = NodeType(
                    id=nodetype.id,
                    name=nodetype.name,
                    parent=self.types[f"{nodetype.parent_id}"],
                )
                self.types[f"{nodetype.parent_id}"].childrens.append(nodetype.id)
            else:
                self.types[f"{nodetype.id}"] = NodeType(nodetype.id, nodetype.name)
        del nodetypes
        gc.collect()
        nodes = await self.app.store.mapAPI.get_all_nodes(page=None, limit=None)
        if nodes:
            for node in nodes.nodes:
                if node.parent_id:
                    self.nodes[f"{node.id}"] = Node(
                        id=node.id,
                        typeNode=self.types[f"{node.type_id}"],
                        x=node.x_cord,
                        y=node.y_cord,
                        z=node.z_cord,
                        parent=self.nodes[f"{node.parent_id}"],
                        depth=self.nodes[f"{node.parent_id}"].depth + 1,
                        name=node.name,
                    )
                    self.nodes[f"{node.parent_id}"].childrens.append(node.id)
                else:
                    self.nodes[f"{node.id}"] = Node(
                        id=node.id,
                        typeNode=self.types[f"{node.type_id}"],
                        x=node.x_cord,
                        y=node.y_cord,
                        z=node.z_cord,
                        depth=1,
                        name=node.name,
                    )
        del nodes
        gc.collect()
        for node_id, node in self.nodes.items():
            conns = await self.app.store.mapAPI.get_all_connections_of_node(int(node_id))
            if conns:
                for conn in conns.conns:
                    self.all_cones[f"{conn.id}"] = Connection(
                        id=conn.id,
                        distance=conn.distance,
                        t_weight=conn.t_weight,
                        time=conn.time,
                    )
                    if conn.node1_id == int(node_id):
                        node.conns[f"{conn.node2_id}"] = self.all_cones[f"{conn.id}"]
                    else:
                        node.conns[f"{conn.node1_id}"] = self.all_cones[f"{conn.id}"]
                    if (
                        self.nodes[f"{conn.node1_id}"].type.name == KEY_TYPES.STREET
                        and self.nodes[f"{conn.node2_id}"].type.name != KEY_TYPES.STREET
                    ):
                        kor = await self.__go_up(KEY_TYPES.KORPUS, self.nodes[f"{conn.node2_id}"])
                        if f"{kor.id}" in self.exits:
                            exits = self.exits[f"{kor.id}"]
                            if f"{conn.node2_id}" not in exits:
                                exits[f"{conn.node2_id}"] = self.nodes[f"{conn.node2_id}"]
                                self.exits[f"{kor.id}"] = exits
                        else:
                            exits = dict()
                            exits[f"{conn.node2_id}"] = self.nodes[f"{conn.node2_id}"]
                            self.exits[f"{kor.id}"] = exits
                        self.exits_list.add(conn.node2_id)
                    elif (
                        self.nodes[f"{conn.node2_id}"].type.name == KEY_TYPES.STREET
                        and self.nodes[f"{conn.node1_id}"].type.name != KEY_TYPES.STREET
                    ):
                        kor = await self.__go_up(KEY_TYPES.KORPUS, self.nodes[f"{conn.node1_id}"])
                        if f"{kor.id}" in self.exits:
                            exits = self.exits[f"{kor.id}"]
                            if f"{conn.node1_id}" not in exits:
                                exits[f"{conn.node1_id}"] = self.nodes[f"{conn.node1_id}"]
                                self.exits[f"{kor.id}"] = exits
                        else:
                            exits = dict()
                            exits[f"{conn.node1_id}"] = self.nodes[f"{conn.node1_id}"]
                            self.exits[f"{kor.id}"] = exits
                        self.exits_list.add(conn.node1_id)
        del conns
        gc.collect()
        self.working = True

    async def __go_up(self, target_class: str, node: Node) -> Node | None:
        current_node = node
        while current_node.type.name != target_class:
            current_node = current_node.parent
        if current_node.type.name == target_class:
            return current_node
        return None

    async def add_type(self, nodetype: NodetypeDC) -> None:
        if nodetype.parent_id:
            self.types[f"{nodetype.id}"] = NodeType(
                id=nodetype.id,
                name=nodetype.name,
                parent=self.types[f"{nodetype.parent_id}"],
            )
        else:
            self.types[f"{nodetype.id}"] = NodeType(nodetype.id, nodetype.name)
        return None

    async def add_node(self, node: NodeDC) -> None:
        if node.parent_id:
            self.nodes[f"{node.id}"] = Node(
                id=node.id,
                typeNode=self.types[f"{node.type_id}"],
                x=node.x_cord,
                y=node.y_cord,
                z=node.z_cord,
                parent=self.nodes[f"{node.parent_id}"],
                depth=self.nodes[f"{node.parent_id}"].depth + 1,
                name=node.name,
            )
        else:
            self.nodes[f"{node.id}"] = Node(
                id=node.id,
                typeNode=self.types[f"{node.type_id}"],
                x=node.x_cord,
                y=node.y_cord,
                z=node.z_cord,
                depth=1,
                name=node.name,
            )
        self.types[f"{node.type_id}"].proto.append(node.id)
        return None

    async def add_conn(self, conn: NodeConnectionDC) -> None:
        self.all_cones[f"{conn.id}"] = Connection(
            id=conn.id,
            distance=conn.distance,
            t_weight=conn.t_weight,
            time=conn.time,
        )
        self.nodes[f"{conn.node1_id}"].conns[f"{conn.node2_id}"] = self.all_cones[
            f"{conn.id}"
        ]
        self.nodes[f"{conn.node2_id}"].conns[f"{conn.node1_id}"] = self.all_cones[
            f"{conn.id}"
        ]
        if (
            self.nodes[f"{conn.node1_id}"].type.name == KEY_TYPES.STREET
            and self.nodes[f"{conn.node2_id}"].type.name != KEY_TYPES.STREET
        ):
            kor = await self.__go_up(KEY_TYPES.KORPUS, self.nodes[f"{conn.node2_id}"])
            if f"{kor.id}" in self.exits:
                exits = self.exits[f"{kor.id}"]
                if f"{conn.node2_id}" not in exits:
                    exits[f"{conn.node2_id}"] = self.nodes[f"{conn.node2_id}"]
                    self.exits[f"{kor.id}"] = exits
            else:
                exits = dict()
                exits[f"{conn.node2_id}"] = self.nodes[f"{conn.node2_id}"]
                self.exits[f"{kor.id}"] = exits
            self.exits_list.add(conn.node2_id)
        elif (
            self.nodes[f"{conn.node2_id}"].type.name == KEY_TYPES.STREET
            and self.nodes[f"{conn.node1_id}"].type.name != KEY_TYPES.STREET
        ):
            kor = await self.__go_up(KEY_TYPES.KORPUS, self.nodes[f"{conn.node1_id}"])
            if f"{kor.id}" in self.exits:
                exits = self.exits[f"{kor.id}"]
                if f"{conn.node1_id}" not in exits:
                    exits[f"{conn.node1_id}"] = self.nodes[f"{conn.node1_id}"]
                    self.exits[f"{kor.id}"] = exits
            else:
                exits = dict()
                exits[f"{conn.node1_id}"] = self.nodes[f"{conn.node1_id}"]
                self.exits[f"{kor.id}"] = exits
            self.exits_list.add(conn.node1_id)
        return None

    async def change_type(self, nodetype: NodetypeDC):
        self.types[f"{nodetype.id}"].name = nodetype.name
        return None

    async def change_node(self, node: NodeDC):
        self.nodes[f"{node.id}"].type = self.types[f"{node.type_id}"]
        self.nodes[f"{node.id}"].x = node.x_cord
        self.nodes[f"{node.id}"].y = node.y_cord
        self.nodes[f"{node.id}"].z = node.z_cord
        return None

    async def change_conn(self, conn: NodeConnectionDC):
        self.all_cones[f"{conn.id}"].distance = conn.distance
        self.all_cones[f"{conn.id}"].time = conn.time
        self.all_cones[f"{conn.id}"].t_weight = conn.t_weight
        return None

    async def delete_conn(self, id: int, node1_id: int, node2_id: int):
        del self.nodes[f"{node1_id}"].conns[f"{node2_id}"]
        del self.nodes[f"{node2_id}"].conns[f"{node1_id}"]
        del self.all_cones[f"{id}"]
        gc.collect()
        return None

    async def delete_node(self, node_id: int):
        for child in self.nodes[f"{node_id}"].children:
            await self.delete_node(child)
        for node2_id, value in self.nodes[f"{node_id}"].conns.items():
            await self.delete_conn(value.id, node_id, node2_id)
        del self.nodes[f"{node_id}"]
        gc.collect()
        return None

    async def delete_type(self, type_id: int):
        for child in self.types[f"{type_id}"].children:
            await self.delete_type(child)
        for node in self.types[f"{type_id}"].proto:
            await self.delete_node(node)
        del self.types[f"{type_id}"]
        gc.collect()
        return None

    @staticmethod
    def __calculate_distance(current: Node, target: Node) -> float:
        return math.sqrt(
            (target.x - current.x)**2
            + (target.y - current.y)**2
            + (target.z - current.z)**2
        )

    async def __navigate_building(self, start_node: int, target_node: int):
        start = self.nodes[f"{start_node}"]
        target = self.nodes[f"{target_node}"]

        to_visit = []
        visited = set()

        heapq.heappush(
            to_visit,
            RouteNode(
                target_distance=self.__calculate_distance(start, target),
                start_distance=0,
                node=start,
                previous=-1,
            ),
        )

        while to_visit:
            current_node = heapq.heappop(to_visit)

            if current_node.current.id == target.id:
                result = list()
                length = current_node.start_distance
                while current_node.previous != -1:
                    result.append(current_node.current)
                    current_node = current_node.previous
                else:
                    result.append(current_node.current)
                return {"result": result[::-1], "length": length}

            visited.add(current_node.current.id)

            for key_node_id, conn_value in current_node.current.conns.items():
                if int(key_node_id) in visited:
                    continue
                if self.nodes[f"{key_node_id}"].type.name == KEY_TYPES.STREET:
                    continue
                if self.nodes[f"{key_node_id}"].type.name == KEY_TYPES.ELEVATOR:
                    continue

                if elem := next(
                    (
                        element
                        for element in to_visit
                        if element.current.id == int(key_node_id)
                    ),
                    None,
                ):
                    if (
                        current_node.start_distance + conn_value.distance
                        < elem.start_distance
                    ):
                        elem.start_distance = (
                            current_node.start_distance + conn_value.distance
                        )
                        elem.previous = current_node
                else:
                    heapq.heappush(
                        to_visit,
                        RouteNode(
                            self.__calculate_distance(
                                self.nodes[f"{key_node_id}"], target
                            ),
                            current_node.start_distance + conn_value.distance,
                            self.nodes[f"{key_node_id}"],
                            current_node,
                        ),
                    )

    async def __navigate_street(self, start_node: int, target_node: int):
        start = self.nodes[f"{start_node}"]
        target = self.nodes[f"{target_node}"]

        to_visit = []
        visited = set()

        heapq.heappush(
            to_visit,
            RouteNode(
                target_distance=self.__calculate_distance(start, target),
                start_distance=0,
                node=start,
                previous=-1,
            ),
        )

        while to_visit:
            current_node = heapq.heappop(to_visit)

            if current_node.current.id == target.id:
                result = list()
                length = current_node.start_distance
                while current_node.previous != -1:
                    result.append(current_node.current)
                    current_node = current_node.previous
                return {"result": result[::-1], "length": length}

            visited.add(current_node.current.id)

            for key_node_id, conn_value in current_node.current.conns.items():
                if int(key_node_id) in visited:
                    continue
                if (
                    self.nodes[f"{key_node_id}"].type.name != KEY_TYPES.STREET
                    or self.nodes[f"{key_node_id}"].type.name != KEY_TYPES.DOOR
                ):
                    continue

                if elem := next(
                    (
                        element
                        for element in to_visit
                        if element.current.id == int(key_node_id)
                    ),
                    None,
                ):
                    if (
                        current_node.start_distance + conn_value.distance
                        < elem.start_distance
                    ):
                        elem.start_distance = (
                            current_node.start_distance + conn_value.distance
                        )
                        elem.previous = current_node
                else:
                    heapq.heappush(
                        to_visit,
                        RouteNode(
                            self.__calculate_distance(
                                self.nodes[f"{key_node_id}"], target
                            ),
                            current_node.start_distance + conn_value.distance,
                            self.nodes[f"{key_node_id}"],
                            current_node,
                        ),
                    )

    async def __navigate_building_elevator(self, start_node: int, target_node: int):
        return None

    async def navigate_main(self, start_node: int, target_node: int):
        start = self.nodes[f"{start_node}"]
        target = self.nodes[f"{target_node}"]

        kor_s = await self.__go_up(KEY_TYPES.KORPUS, start)
        kor_t = await self.__go_up(KEY_TYPES.KORPUS, target)

        if kor_s == kor_t:
            result = await self.__navigate_building(start_node, target_node)
            return result["result"]
        elif kor_s is None:
            if kor_t is None:
                result = await self.__navigate_street(start_node, target_node)
                return result["result"]
            else:
                entrances = self.exits[f"{kor_t.id}"]
                best_street_route = None
                route_length = -1
                optimal_entrance = -1
                for key in entrances:
                    temp_result = await self.__navigate_street(start_node, int(key))
                    if optimal_entrance == -1 or temp_result < route_length:
                        best_street_route = temp_result["result"]
                        route_length = temp_result.length
                        optimal_entrance = int(key)
                building_route = await self.__navigate_building(
                    optimal_entrance, target_node
                )
                return best_street_route[:-1] + building_route["result"]
        elif kor_t is None:
            exits = self.exits[f"{kor_s.id}"]
            best_street_route = None
            route_length = -1
            optimal_exit = -1
            for key in exits:
                temp_result = await self.__navigate_street(int(key), target_node)
                if optimal_exit == -1 or temp_result < route_length:
                    best_street_route = temp_result["result"]
                    route_length = temp_result.length
                    optimal_exit = int(key)
            building_route = await self.__navigate_building(start_node, optimal_exit)
            return building_route["result"][:-1] + best_street_route
        else:
            exits_s = self.exits[f"{kor_s.id}"]
            exits_t = self.exits[f"{kor_t.id}"]
            best_street_route = None
            route_length = -1
            optimal_exit_s = -1
            optimal_exit_t = -1
            for key_s in exits_s:
                for key_t in exits_t:
                    temp_result = await self.__navigate_street(int(key_s), int(key_t))
                if optimal_exit_s == -1 or temp_result < route_length:
                    best_street_route = temp_result["result"]
                    route_length = temp_result.length
                    optimal_exit_s = int(key_s)
                    optimal_exit_t = int(key_t)
            building_route_s = await self.__navigate_building(start_node, optimal_exit_s)
            building_route_t = await self.__navigate_building(optimal_exit_t, target_node)
            return building_route_s["result"][:-1] + best_street_route["result"][:-1] + building_route_t
