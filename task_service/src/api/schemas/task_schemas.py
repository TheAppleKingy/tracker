from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreateSchema(BaseModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=500)
    deadline: Optional[datetime] = None
    user_id: int
    task_id: Optional[int] = None


class TaskUpdateSchema(BaseModel):
    title: Optional[str] = Field(max_length=100, default=None)
    description: Optional[str] = Field(max_length=500, default=None)
    deadline: Optional[datetime] = None
    done: Optional[bool] = False
    user_id: Optional[int] = None
    task_id: Optional[int] = None


class TaskViewSchema(BaseModel):
    id: int
    title: str
    description: str
    creation_date: datetime
    deadline: datetime
    pass_date: Optional[datetime]
    done: bool
    user_id: int
    task_id: Optional[int] = None


class TaskTreeSchema(TaskViewSchema):
    subtasks: list['TaskTreeSchema']


class TaskViewForUserSchema(BaseModel):
    id: int
    title: str
    description: str
    creation_date: datetime
    deadline: datetime
    pass_date: Optional[datetime]
    done: bool
    subtasks: list['TaskViewForUserSchema']

    class Config:
        orm_mode = True


class TaskCreateForUserSchema(BaseModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=500)
    deadline: Optional[datetime] = None
    task_id: Optional[int] = None


class TaskUpdateForUserSchema(BaseModel):
    title: Optional[str] = Field(max_length=100, default=None)
    description: Optional[str] = Field(max_length=500, default=None)
    deadline: Optional[datetime] = None
    done: Optional[bool] = False
    task_id: Optional[int] = None
