from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String)

class Training(Base):
    __tablename__ = "trainings"
    id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String)
    course_name = Column(String)
    provider = Column(String)
    level = Column(String)