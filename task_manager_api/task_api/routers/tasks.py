from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from database import get_db
from models import Task, User, TaskStatus, TaskPriority
from schemas import TaskCreate, TaskUpdate, TaskOut, PaginatedTasks
from auth_utils import get_current_user

router = APIRouter()

@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task for the authenticated user."""
    task = Task(**task_data.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/", response_model=PaginatedTasks)
async def list_tasks(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    status: Optional[TaskStatus] = Query(default=None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(default=None, description="Filter by priority"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all tasks for the authenticated user with pagination and filters."""
    filters = [Task.owner_id == current_user.id, Task.is_deleted == False]
    if status:
        filters.append(Task.status == status)
    if priority:
        filters.append(Task.priority == priority)

    query = db.query(Task).filter(and_(*filters))
    total = query.count()
    tasks = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedTasks(total=total, page=page, page_size=page_size, items=tasks)

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task by ID."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id,
        Task.is_deleted == False
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Partially update a task (only provided fields are updated)."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id,
        Task.is_deleted == False
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft-delete a task (data is preserved in DB, not shown in queries)."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id,
        Task.is_deleted == False
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_deleted = True
    db.commit()
