from sqlalchemy import Column, Integer, String, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'


# Define the Skill model
class Skill(Base):
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True)
    skill_name = Column(String, nullable=False)


# Define the Department model
class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    department_name = Column(String, nullable=False)


# Association table for the many-to-many relationship between User and Skill
employee_skills = Table(
    'employee_skills',
    Base.metadata,
    Column('employee_id', ForeignKey('employee.id'), primary_key=True),
    Column('skill_id', ForeignKey('skills.id'), primary_key=True)
)


# Define the User model
class User(Base):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    login = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "login": self.login,
            "email": self.email,
            "phone": self.phone,
            "role": self.role.name,  # Assuming role is an Enum and you want to return its value
        }

    department_id = Column(Integer, ForeignKey('departments.id'))
    department = relationship('Department', back_populates='employees')

    skills = relationship('Skill', secondary=employee_skills, back_populates='users')


Department.employees = relationship('User', back_populates='department')
Skill.users = relationship('User', secondary=employee_skills, back_populates='skills')



