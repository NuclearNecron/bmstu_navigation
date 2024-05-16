from dataclasses import dataclass
import datetime



@dataclass
class NodetypeDC:
    id: int
    parent_id: int | None
    name: str
    shortname: str
    description: str | None


@dataclass
class NodeDC:
    id: int
    parent_id: int | None
    creator_id: int
    editor_id: int
    created_time: datetime
    edited_time: datetime
    type_id: int
    name: str
    shortname: str
    description: str | None
    x_cord: float
    y_cord: float
    z_cord: float


@dataclass
class NodeConnectionDC:
    id: int
    node1_id: int
    node2_id: int
    distance: float
    time: float
    t_weight: float


@dataclass
class NodesDC:
    nodes: list[NodeDC]


@dataclass
class TypesDC:
    types: list[NodetypeDC]


@dataclass
class ConnectionsDC:
    conns: list[NodeConnectionDC]
