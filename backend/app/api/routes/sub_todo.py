import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import SubTodo, SubTodoCreate, SubTodoPublic, SubTodosPublic, SubTodoUpdate, Message, Todo

router = APIRouter(prefix="/subtodos", tags=["subtodos"])


@router.get("/", response_model=SubTodosPublic)
def read_sub_todos(
    session: SessionDep, current_user: CurrentUser, todo_id=uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve sub todos.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(SubTodo)
        count = session.exec(count_statement).one()
        statement = select(SubTodo).offset(skip).limit(limit)
        todos = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(SubTodo)
            .where(SubTodo.todo_id == todo_id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(SubTodo)
            .where(SubTodo.todo_id == todo_id)
            .offset(skip)
            .limit(limit)
        )
        todos = session.exec(statement).all()

    return SubTodosPublic(data=todos, count=count)


@router.get("/{id}", response_model=SubTodoPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get sub todo by ID.
    """
    sub_todo = session.get(SubTodo, id)
    if not sub_todo:
        raise HTTPException(status_code=404, detail="Sub todo not found")
    return sub_todo

@router.post("/", response_model=SubTodoPublic)
def create_sub_todo(
    *, session: SessionDep, sub_todo_in: SubTodoCreate
) -> Any:
    """
    Create new sub todo.
    """
    todo = session.get(Todo, sub_todo_in.todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    sub_todo = SubTodoCreate.model_validate(sub_todo_in)
    create_todo = SubTodo(**dict(sub_todo))
    session.add(create_todo)
    session.commit()
    session.refresh(create_todo)
    return create_todo


# @router.put("/{id}", response_model=SubTodoPublic)
# def update_sub_todo(
#     *,
#     session: SessionDep,
#     current_user: CurrentUser,
#     id: uuid.UUID,
#     todo_in: SubTodoUpdate,
# ) -> Any:
#     """
#     Update an item.
#     """
#     sub_todo = session.get(SubTodo, id)
#     if not sub_todo:
#         raise HTTPException(status_code=404, detail="SubTodo not found")
#     if not current_user.is_superuser and (sub_todo.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     update_dict = todo_in.model_dump(exclude_unset=True)
#     sub_todo.sqlmodel_update(update_dict)
#     session.add(sub_todo)
#     session.commit()
#     session.refresh(sub_todo)
#     return sub_todo

@router.put("/{id}", response_model=SubTodoPublic)
def update_sub_todo(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    sub_todo_in: SubTodoUpdate,
) -> Any:
    """
    Update a sub todo by ID.
    """
    # Fetch the sub todo by ID
    sub_todo = session.get(SubTodo, id)
    if not sub_todo:
        raise HTTPException(status_code=404, detail="SubTodo not found")
    
    # Fetch the associated parent todo for ownership verification
    parent_todo = session.get(Todo, sub_todo.todo_id)
    if not parent_todo:
        raise HTTPException(status_code=404, detail="Parent Todo not found")
    
    # Permission check: Ensure the user is the owner or a superuser
    if not current_user.is_superuser and (parent_todo.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update the SubTodo with the new data
    update_data = sub_todo_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sub_todo, key, value)
    
    # Commit changes to the database
    session.add(sub_todo)
    session.commit()
    session.refresh(sub_todo)
    
    return sub_todo

@router.delete("/{id}")
def delete_sub_todo(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a sub todo.
    """
    sub_todo = session.get(SubTodo, id)
    if not sub_todo:
        raise HTTPException(status_code=404, detail="SubTodo not found")
    todo = session.get(Todo, sub_todo.todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if not current_user.is_superuser and (todo.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(sub_todo)
    session.commit()
    return Message(message="SubTodo deleted successfully")
