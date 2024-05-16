from app.base.db import db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.user.dataclasses import AccessClassDC, UserAccessDC


class UserModel(db):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)

    access = relationship(
        "UserAccessModel",
        back_populates="user",
        foreign_keys="UserAccessModel.user_id",
    )
    usermade = relationship(
        "NodeModel", back_populates="usermade", foreign_keys="NodeModel.creator_id"
    )
    useredit = relationship(
        "NodeModel", back_populates="useredit", foreign_keys="NodeModel.editor_id"
    )


class AccessClassModel(db):
    __tablename__ = "accessclass"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

    accessgiven = relationship(
        "UserAccessModel",
        back_populates="accessgiven",
        foreign_keys="UserAccessModel.access_id",
    )

    def to_dc(self) -> AccessClassDC:
        return AccessClassDC(
            id=self.id,
            name=self.name,
        )


class UserAccessModel(db):
    __tablename__ = "useraccess"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="cascade"), nullable=False)
    access_id = Column(
        Integer,
        ForeignKey("accessclass.id", ondelete="cascade"),
        nullable=False,
    )
    date = Column(DateTime, nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "access_id", name="_user_access_uc"),)
    user = relationship(
        "UserModel",
        back_populates="access",
        foreign_keys="UserAccessModel.user_id",
    )
    accessgiven = relationship(
        "AccessClassModel",
        back_populates="accessgiven",
        foreign_keys="UserAccessModel.access_id",
    )

    def to_dc(self) -> UserAccessDC:
        return UserAccessDC(
            id=self.id,
            access_id=self.access_id,
            date=self.date,
            user_id=self.user_id,
        )
