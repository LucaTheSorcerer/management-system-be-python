import asyncio

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from database import SessionLocal
from entities.models import Department, User  # Ensure import paths are correct
from pydantic import BaseModel
from typing import List, Dict
from DepartmentService import DepartmentService
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound


from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DepartmentBase(BaseModel):
    department_name: str


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentRead(DepartmentBase):
    id: int

    class Config:
        orm_mode = True


class DepartmentUpdate(BaseModel):
    department_name: str


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


@app.post("/departments/", response_model=DepartmentCreate, status_code=status.HTTP_201_CREATED)
async def create_department(department: DepartmentCreate, db: AsyncSession = Depends(get_db)):
    dept_service = DepartmentService(db)
    try:
        return await dept_service.create_department(department.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/departments/{department_id}", response_model=DepartmentCreate)
async def get_department(department_id: int, db: AsyncSession = Depends(get_db)):
    dept_service = DepartmentService(db)
    try:
        return await dept_service.get_department_by_id(department_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



# @app.put("/departments/{department_id}", response_model=DepartmentRead)
# async def update_department(department_id: int, department_data: DepartmentUpdate, db: AsyncSession = Depends(get_db)):
#     async with db as session:
#         stmt = select(Department).where(Department.id == department_id)
#         result = await session.execute(stmt)
#         department = result.scalars().first()
#         if not department:
#             raise HTTPException(status_code=404, detail="Department not found")
#
#         department.department_name = department_data.department_name
#         session.add(department)
#         await session.commit()
#         await session.refresh(department)  # Ensure data is reloaded after commit if needed
#
#         # Manual conversion to dictionary if Pydantic's orm_mode isn't sufficient
#         department_dict = {
#             "id": department.id,
#             "department_name": department.department_name
#         }
#         return department_dict



@app.put("/departments/{department_id}", response_model=DepartmentRead)
async def update_department(department_id: int, department_data: DepartmentUpdate, db: AsyncSession = Depends(get_db)):
    async with db.begin():  # This will manage the transaction implicitly
        try:
            stmt = select(Department).where(Department.id == department_id).with_for_update()
            result = await db.execute(stmt)
            department = result.scalars().one()  # This will automatically raise NoResultFound if not found

            department.department_name = department_data.department_name

            # The transaction will commit at the end of the 'async with' block if no exceptions are raised
            department_dict = {
                "id": department.id,
                "department_name": department.department_name
            }
            return department_dict
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/departments/dirty-read/{department_id}", response_model=DepartmentRead)
async def get_department_dirty_read(department_id: int, db: AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            stmt = select(Department).where(Department.id == department_id)
            result = await db.execute(stmt)
            department = result.scalars().one()
            return department
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@app.get("/departments/", response_model=List[DepartmentRead])
async def get_all_departments(db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Department).options(joinedload(Department.employees)))
        departments = result.scalars().all()
        return departments


@app.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(department_id: int, db: AsyncSession = Depends(get_db)):
    dept_service = DepartmentService(db)
    try:
        await dept_service.delete_department(department_id)
        return {}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Assuming you have an endpoint like this
@app.put("/departments/concurrent/{department_id}")
async def update_department_concurrently(department_id: int, db: AsyncSession = Depends(get_db)):
    dept_service = DepartmentService(db)
    # First update
    await dept_service.update_department(department_id, {"department_name": "New Name 1"})
    # Simulated delay to allow Java to update concurrently
    # await asyncio.sleep(5)
    # Second update
    return await dept_service.update_department(department_id, {"department_name": "New Name 2"})


@app.get("/users/")
async def read_users(db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return {"users": [user.to_dict() for user in users]}  # Assuming a `to_dict()` method on your User model



@app.put("/departments/concurrent-update/{department_id}", response_model=DepartmentRead)
async def concurrent_update_department(department_id: int, db: AsyncSession = Depends(get_db)):
    dept_service = DepartmentService(db)
    try:
        # First update
        await dept_service.update_department(department_id, {"department_name": "Python Update 1"})
        # Simulated delay to allow Java to update concurrently
        await asyncio.sleep(1)
        # Second update
        return await dept_service.update_department(department_id, {"department_name": "Python Update 2"})
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))




@app.put("/departments/dirty-update/{department_id}", response_model=DepartmentRead)
async def dirty_update_department(department_id: int, department_data: DepartmentUpdate, db: AsyncSession = Depends(get_db)):
    async with db.begin():  # This will manage the transaction implicitly
        try:
            stmt = select(Department).where(Department.id == department_id).with_for_update()
            result = await db.execute(stmt)
            department = result.scalars().one()  # This will automatically raise NoResultFound if not found

            department.department_name = department_data.department_name
            await db.flush()  # Apply changes but do not commit
            await asyncio.sleep(10)  # Sleep to simulate delay and allow dirty read

            # The transaction will commit at the end of the 'async with' block if no exceptions are raised
            department_dict = {
                "id": department.id,
                "department_name": department.department_name
            }
            return department_dict
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))