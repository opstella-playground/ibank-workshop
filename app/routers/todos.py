"""Todo API router with CRUD operations."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import desc, select

from app.database import SessionDep
from app.models.todo import Todo, TodoCreate, TodoPublic, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoPublic, status_code=201)
def create_todo(todo: TodoCreate, session: SessionDep) -> Todo:
    """Create a new todo item."""
    db_todo = Todo.model_validate(todo)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


@router.get("/", response_model=list[TodoPublic])
def read_todos(
    session: SessionDep,
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    limit: Annotated[int, Query(le=100, description="Max items to return")] = 20,
    completed: bool | None = Query(
        default=None, description="Filter by completion status"
    ),
) -> list[Todo]:
    """Get all todos with optional filtering and pagination."""
    query = select(Todo)

    if completed is not None:
        query = query.where(Todo.completed == completed)

    query = query.offset(offset).limit(limit).order_by(desc(Todo.created_at))
    todos = session.exec(query).all()
    return list(todos)


@router.get("/{todo_id}", response_model=TodoPublic)
def read_todo(todo_id: int, session: SessionDep) -> Todo:
    """Get a specific todo by ID."""
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.patch("/{todo_id}", response_model=TodoPublic)
def update_todo(todo_id: int, todo_update: TodoUpdate, session: SessionDep) -> Todo:
    """Update a todo item (partial update)."""
    db_todo = session.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    update_data = todo_update.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.now(UTC)
        db_todo.sqlmodel_update(update_data)
        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)

    return db_todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, session: SessionDep) -> None:
    """Delete a todo item."""
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    session.delete(todo)
    session.commit()
