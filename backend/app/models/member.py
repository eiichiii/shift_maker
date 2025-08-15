from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..db import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    gender = Column(String, nullable=False)  # 'M' or 'F'
    is_committee = Column(Boolean, default=False, nullable=False)
    
    availabilities = relationship("Availability", back_populates="member", cascade="all, delete-orphan")