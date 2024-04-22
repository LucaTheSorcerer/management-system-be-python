# services.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from entities.models import Department

class DepartmentService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_department(self, department_data: dict):
        department = Department(**department_data)
        self.db_session.add(department)
        await self.db_session.commit()
        await self.db_session.refresh(department)
        return department

    async def get_department_by_id(self, department_id: int):
        query = select(Department).where(Department.id == department_id)
        result = await self.db_session.execute(query)
        try:
            return result.scalars().one()
        except NoResultFound:
            raise ValueError("Department not found")

    async def update_department(self, department_id: int, department_data: dict):
        department = await self.get_department_by_id(department_id)
        for key, value in department_data.items():
            setattr(department, key, value)
        await self.db_session.commit()
        return department

    async def get_all_departments(self):
        query = select(Department)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def delete_department(self, department_id: int):
        department = await self.get_department_by_id(department_id)
        await self.db_session.delete(department)
        await self.db_session.commit()
