"""Todo model definitions using SQLModel."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class TodoBase(SQLModel):
    """Base Todo model with common fields."""

    title: str = Field(min_length=1, max_length=200, description="Todo title")
    description: str | None = Field(
        default=None, max_length=1000, description="Todo description"
    )
    completed: bool = Field(default=False, description="Whether the todo is completed")
    priority: int = Field(
        default=1, ge=1, le=5, description="Priority level from 1 (low) to 5 (high)"
    )


class Todo(TodoBase, table=True):
    """Todo database model."""

    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TodoCreate(TodoBase):
    """Schema for creating a new Todo."""


class TodoUpdate(SQLModel):
    """Schema for updating a Todo (all fields optional)."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool | None = None
    priority: int | None = Field(default=None, ge=1, le=5)


class TodoPublic(TodoBase):
    """Schema for returning Todo in API responses."""

    id: int
    created_at: datetime
    updated_at: datetime
