from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.production_line import ProductionLine
from app.schemas.production_line import ProductionLineCreate, ProductionLineUpdate
from typing import List, Optional, Dict, Any
import logging

# 配置日志
logger = logging.getLogger(__name__)

class ProductionLineService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_name(self, name: str) -> Optional[ProductionLine]:
        """根据名称获取生产线"""
        try:
            return self.db.query(ProductionLine).filter(ProductionLine.name == name).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error when getting production line by name '{name}': {str(e)}")
            raise
    
    def get(self, id: int) -> Optional[ProductionLine]:
        """根据ID获取生产线"""
        try:
            return self.db.query(ProductionLine).filter(ProductionLine.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error when getting production line by ID {id}: {str(e)}")
            raise
    
    
    def search_production_lines(self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> List[ProductionLine]:
        try:
            query = self.db.query(ProductionLine)
            
            if filters:
                if 'enabled' in filters and filters['enabled'] is not None:
                    query = query.filter(ProductionLine.enabled == filters['enabled'])
                if 'status' in filters and filters['status']:
                    query = query.filter(ProductionLine.status == filters['status'])
                if 'name' in filters and filters['name']:
                    query = query.filter(ProductionLine.name.ilike(f"%{filters['name']}%"))
                if 'description' in filters and filters['description']:
                    query = query.filter(ProductionLine.description.ilike(f"%{filters['description']}%"))
            
            return query.order_by(ProductionLine.name).offset(skip).limit(limit).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error when searching production lines: {str(e)}")
            raise
    
    def get_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        try:
            query = self.db.query(ProductionLine)
            
            if filters:
                if 'enabled' in filters and filters['enabled'] is not None:
                    query = query.filter(ProductionLine.enabled == filters['enabled'])
                if 'status' in filters and filters['status']:
                    query = query.filter(ProductionLine.status == filters['status'])
                if 'name' in filters and filters['name']:
                    query = query.filter(ProductionLine.name.ilike(f"%{filters['name']}%"))
                if 'description' in filters and filters['description']:
                    query = query.filter(ProductionLine.description.ilike(f"%{filters['description']}%"))
            
            return query.count()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error when counting production lines: {str(e)}")
            raise
    
    def create(self, obj_in: ProductionLineCreate) -> ProductionLine:
        try:
            db_obj = ProductionLine(**obj_in.model_dump())
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Created production line: {db_obj.name} (ID: {db_obj.id})")
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error when creating production line: {str(e)}")
            raise
    
    def update(self, db_obj: ProductionLine, obj_in: ProductionLineUpdate) -> ProductionLine:
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Updated production line {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error when updating production line {db_obj.id}: {str(e)}")
            raise
    
    def delete(self, id: int) -> ProductionLine:
        try:
            obj = self.db.query(ProductionLine).get(id)
            if obj:
                self.db.delete(obj)
                self.db.commit()
                logger.info(f"Deleted production line {id}")
                return obj
            else:
                logger.warning(f"Production line {id} not found for deletion")
                raise ValueError(f"Production line {id} not found")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error when deleting production line {id}: {str(e)}")
            raise
    
    def get_enabled_lines(self) -> List[ProductionLine]:
        try:
            return self.db.query(ProductionLine).filter(ProductionLine.enabled == True).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error when getting enabled production lines: {str(e)}")
            raise
    
    def get_lines_by_status(self, status: str) -> List[ProductionLine]:
        try:
            return self.db.query(ProductionLine).filter(ProductionLine.status == status).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error when getting production lines by status '{status}': {str(e)}")
            raise
