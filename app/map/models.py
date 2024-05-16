from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.base.db import db
from app.map.dataclasses import NodeDC, NodetypeDC, NodeConnectionDC


class NodeModel(db):
    __tablename__ = "node"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    shortname = Column(String, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("node.id", ondelete="cascade"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    editor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_time = Column(DateTime, nullable=False)
    edited_time = Column(DateTime, nullable=False)
    type_id = Column(Integer, ForeignKey("type.id", ondelete="cascade"), nullable=False)
    description = Column(String, nullable=True)
    x_cord = Column(Float, nullable=False)
    y_cord = Column(Float, nullable=False)
    z_cord = Column(Float, nullable=False)

    children = relationship("NodeModel")
    usermade = relationship(
        "UserModel", back_populates="usermade", foreign_keys="NodeModel.creator_id"
    )
    nodetype = relationship(
        "TypeModel", back_populates="nodetype", foreign_keys="NodeModel.type_id"
    )
    node1 = relationship(
        "ConnectionModel", back_populates="node1", foreign_keys="ConnectionModel.node1_id"
    )
    node2 = relationship(
        "ConnectionModel", back_populates="node2", foreign_keys="ConnectionModel.node2_id"
    )
    useredit = relationship(
        "UserModel", back_populates="useredit", foreign_keys="NodeModel.editor_id"
    )

    def to_dc(self) -> NodeDC:
        return NodeDC(
            id=self.id,
            parent_id=self.parent_id,
            creator_id=self.creator_id,
            editor_id=self.editor_id,
            created_time=self.created_time,
            edited_time=self.edited_time,
            type_id=self.type_id,
            name=self.name,
            shortname=self.shortname,
            description=self.description,
            x_cord=self.x_cord,
            y_cord=self.y_cord,
            z_cord=self.z_cord,
        )


class TypeModel(db):
    __tablename__ = "type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    shortname = Column(String, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("type.id", ondelete="cascade"), nullable=True)
    description = Column(String, nullable=True)

    children = relationship("TypeModel")
    nodetype = relationship(
        "NodeModel", back_populates="nodetype", foreign_keys="NodeModel.type_id"
    )

    def to_dc(self) -> NodetypeDC:
        return NodetypeDC(
            id=self.id,
            name=self.name,
            parent_id=self.parent_id,
            description=self.description,
            shortname=self.shortname,
        )


class ConnectionModel(db):
    __tablename__ = "connection"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node1_id = Column(Integer, ForeignKey("node.id", ondelete="cascade"), nullable=False)
    node2_id = Column(Integer, ForeignKey("node.id", ondelete="cascade"), nullable=False)
    distance = Column(Float, nullable=False)
    time = Column(Float, nullable=False)
    t_weight = Column(Float, nullable=False)

    __tableargs__ = (UniqueConstraint("node1_id", "node2_id", name="node_combination"),)

    node1 = relationship(
        "NodeModel", back_populates="node1", foreign_keys="ConnectionModel.node1_id"
    )
    node2 = relationship(
        "NodeModel", back_populates="node2", foreign_keys="ConnectionModel.node2_id"
    )

    def to_dc(self) -> NodeConnectionDC:
        return NodeConnectionDC(
            id=self.id,
            node1_id=self.node1_id,
            node2_id=self.node2_id,
            distance=self.distance,
            time=self.time,
            t_weight=self.t_weight,
        )
