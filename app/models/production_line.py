from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class ProductionLine(Base):
    __tablename__ = "production_lines"
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # 数据库自增主键
    name = Column(String, nullable=False, unique=True, index=True)  # 生产线名称
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    
    # Store the status as a string in the database
    status = Column(String, nullable=False, default="idle")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
