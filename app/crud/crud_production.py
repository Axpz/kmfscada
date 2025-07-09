from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.production import Production
from app.schemas.production import ProductionCreate, ProductionUpdate


class CRUDProduction(CRUDBase[Production, ProductionCreate, ProductionUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Production]:
        return db.query(Production).filter(Production.name == name).first()

    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Production]:
        return (
            db.query(Production)
            .filter(Production.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(self, db: Session, *, status: str, skip: int = 0, limit: int = 100) -> List[Production]:
        return (
            db.query(Production)
            .filter(Production.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )


production = CRUDProduction(Production) 