from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .associations import users_groups
from .tasks import Base


class User(Base):
    __tablename__ = 'users'
    tg_name: Mapped[str] = mapped_column(
        String(50), unique=True)
    email: Mapped[str] = mapped_column(
        String(50), unique=True)
    password: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    groups: Mapped[list['Group']] = relationship(secondary=users_groups,
                                                 back_populates='users', lazy='selectin', passive_deletes=True)
    tasks: Mapped[list['Task']] = relationship(
        back_populates='user', cascade='all, delete-orphan', lazy='selectin')


class Group(Base):
    __tablename__ = 'groups'
    title: Mapped[str] = mapped_column(String(20))
    users: Mapped[list['User']] = relationship(secondary=users_groups,
                                               back_populates='groups', lazy='selectin', passive_deletes=True)


"""By models/methods perms may be added"""
