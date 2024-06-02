class NodeType:

    def __init__(self, id: int, name: str, **kwargs):
        self.id = id
        if kwargs:
            if kwargs.get("parent"):
                self.parent = kwargs.get("parent")
            else:
                self.parent = None
        self.name = name
        self.childrens = []
        self.proto = []


class Node:

    def __init__(
        self,
        id: int,
        typeNode: NodeType,
        x: float,
        y: float,
        z: float,
        depth: int,
        name: str,
        **kwargs,
    ):
        self.id = id
        if kwargs:
            if kwargs.get("parent"):
                self.parent = kwargs.get("parent")
            else:
                self.parent = None
        self.type = typeNode
        self.x = x
        self.y = y
        self.z = z
        self.conns = dict()
        self.depth = depth
        self.childrens = []
        self.name = name

    def __lt__(self, other):
        return self.id < other.id


class Connection:

    def __init__(self, id: int, distance: float, time: float, t_weight: float):
        self.id = id
        self.distance = distance
        self.time = time
        self.t_weight = t_weight


class RouteNode:

    def __init__(
        self, target_distance: float, start_distance: float, node: Node, previous
    ):
        self.target_distance = target_distance
        self.start_distance = start_distance
        self.current = node
        self.previous = previous

    def __lt__(self, other):
        if self.target_distance+self.start_distance != other.target_distance+self.start_distance:
            return self.target_distance+self.start_distance < other.target_distance+self.start_distance
        return self.current < other.current
