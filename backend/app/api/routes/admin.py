from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session
from app.core.engine import engine
from app.models.user import User
from app.core.security import get_current_active_user
import pprint

router = APIRouter()
pp = pprint.PrettyPrinter(indent=2)

@router.get("/inspect-db")
def print_and_return_selected_tables(current_user: User = Depends(get_current_active_user)):
    # if not current_user.is_superuser: - PLEASEREMOVEPLEASE
    #     raise HTTPException(status_code=403, detail="Admins only")

    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    result = {}

    with Session(engine) as session:
        for table in table_names:
            print(f"\nDEVELOPMENT ONLY _________ TABLE: {table}") 
            try:
                rows = session.exec(text(f'SELECT * FROM "{table}"')).fetchall()
                if not rows:
                    print("(empty)")
                    result[table] = []
                else:
                    row_dicts = [dict(row._mapping) for row in rows]
                    for row in row_dicts:
                        pp.pprint(row)
                    result[table] = row_dicts
            except SQLAlchemyError as e:
                error_msg = f"Error reading table {table}: {e}"
                print(error_msg)
                result[table] = error_msg

    return result
