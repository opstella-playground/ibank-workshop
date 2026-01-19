"""Todo API router with CRUD operations.

This module demonstrates logging best practices for API endpoints:
- INFO level for successful operations
- WARNING level for expected errors (e.g., not found)
- ERROR level for unexpected errors
- DEBUG level for detailed operation info
"""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import desc, select

from app.database import SessionDep
from app.logging_config import get_logger
from app.models.todo import Todo, TodoCreate, TodoPublic, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])

# Get logger for this module
logger = get_logger("routers.todos")


@router.post("/", response_model=TodoPublic, status_code=201)
def create_todo(todo: TodoCreate, session: SessionDep) -> Todo:
    """Create a new todo item."""
    # DEBUG: Log incoming request details
    logger.debug(
        f"Creating new todo: {todo.title}",
        extra={"action": "todo_create_start", "title": todo.title},
    )

    db_todo = Todo.model_validate(todo)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    # INFO: Log successful creation
    logger.info(
        f"Todo created successfully: id={db_todo.id}",
        extra={
            "action": "todo_created",
            "todo_id": db_todo.id,
            "title": db_todo.title,
        },
    )

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
    # DEBUG: Log query parameters
    logger.debug(
        f"Fetching todos with offset={offset}, limit={limit}, completed={completed}",
        extra={
            "action": "todos_list_start",
            "offset": offset,
            "limit": limit,
            "completed_filter": completed,
        },
    )

    query = select(Todo)

    if completed is not None:
        query = query.where(Todo.completed == completed)

    query = query.offset(offset).limit(limit).order_by(desc(Todo.created_at))
    todos = session.exec(query).all()

    # INFO: Log successful fetch with count
    logger.info(
        f"Retrieved {len(todos)} todos",
        extra={
            "action": "todos_listed",
            "count": len(todos),
            "offset": offset,
            "limit": limit,
        },
    )

    return list(todos)


@router.get("/{todo_id}", response_model=TodoPublic)
def read_todo(todo_id: int, session: SessionDep) -> Todo:
    """Get a specific todo by ID."""
    logger.debug(
        f"Fetching todo id={todo_id}",
        extra={"action": "todo_get_start", "todo_id": todo_id},
    )

    todo = session.get(Todo, todo_id)
    if not todo:
        # WARNING: Expected error (not found) - use WARNING level
        logger.warning(
            f"Todo not found: id={todo_id}",
            extra={"action": "todo_not_found", "todo_id": todo_id},
        )
        raise HTTPException(status_code=404, detail="Todo not found")

    logger.debug(
        f"Todo retrieved: id={todo_id}",
        extra={"action": "todo_retrieved", "todo_id": todo_id},
    )

    return todo


@router.patch("/{todo_id}", response_model=TodoPublic)
def update_todo(todo_id: int, todo_update: TodoUpdate, session: SessionDep) -> Todo:
    """Update a todo item (partial update)."""
    logger.debug(
        f"Updating todo id={todo_id}",
        extra={
            "action": "todo_update_start",
            "todo_id": todo_id,
            "update_fields": list(todo_update.model_dump(exclude_unset=True).keys()),
        },
    )

    db_todo = session.get(Todo, todo_id)
    if not db_todo:
        logger.warning(
            f"Cannot update: Todo not found id={todo_id}",
            extra={"action": "todo_update_not_found", "todo_id": todo_id},
        )
        raise HTTPException(status_code=404, detail="Todo not found")

    update_data = todo_update.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.now(UTC)
        db_todo.sqlmodel_update(update_data)
        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)

        # INFO: Log what was updated
        logger.info(
            f"Todo updated: id={todo_id}",
            extra={
                "action": "todo_updated",
                "todo_id": todo_id,
                "updated_fields": list(update_data.keys()),
            },
        )
    else:
        logger.debug(
            f"No changes for todo id={todo_id}",
            extra={"action": "todo_no_changes", "todo_id": todo_id},
        )

    return db_todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, session: SessionDep) -> None:
    """Delete a todo item."""
    logger.debug(
        f"Deleting todo id={todo_id}",
        extra={"action": "todo_delete_start", "todo_id": todo_id},
    )

    todo = session.get(Todo, todo_id)
    if not todo:
        logger.warning(
            f"Cannot delete: Todo not found id={todo_id}",
            extra={"action": "todo_delete_not_found", "todo_id": todo_id},
        )
        raise HTTPException(status_code=404, detail="Todo not found")

    session.delete(todo)
    session.commit()

    # INFO: Log successful deletion
    logger.info(
        f"Todo deleted: id={todo_id}",
        extra={"action": "todo_deleted", "todo_id": todo_id, "title": todo.title},
    )

