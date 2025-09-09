from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
import logging
from app.api import deps
from app.services.production_line_service import ProductionLineService
from app.schemas.production_line import (
    ProductionLineCreate, 
    ProductionLineUpdate, 
    ProductionLineInDB,
    ProductionLineFilter,
    ProductionLineListResponse
)

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/list", response_model=ProductionLineListResponse, summary="获取生产线列表")
async def list_production_lines(
    *,
    db: Session = Depends(deps.get_db),
    filters: ProductionLineFilter = Body(default=ProductionLineFilter())
) -> ProductionLineListResponse:
    try:
        logger.info(f"Fetching production lines with filters: {filters}")
        
        service = ProductionLineService(db)
        
        # 构建查询条件
        query_filters = {}
        if filters.enabled is not None:
            query_filters['enabled'] = filters.enabled
        if filters.status:
            query_filters['status'] = filters.status
        if filters.name:
            query_filters['name'] = filters.name
        if filters.description:
            query_filters['description'] = filters.description
        
        # 计算分页
        skip = (filters.page - 1) * filters.size
        
        # 获取数据
        lines = service.search_production_lines(
            skip=skip, 
            limit=filters.size, 
            filters=query_filters
        )
        
        # 获取总数
        total = service.get_count(filters=query_filters)
        
        logger.info(f"Found {total} production lines, returning page {filters.page} with {len(lines)} items")
        
        return ProductionLineListResponse(
            items=lines,
            total=total,
            page=filters.page,
            size=filters.size
        )
        
    except Exception as e:
        logger.error(f"Error fetching production lines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取生产线列表失败"
        )

@router.post("/", response_model=ProductionLineInDB, status_code=status.HTTP_201_CREATED, summary="创建新生产线")
async def create_production_line(
    *,
    db: Session = Depends(deps.get_db),
    line_in: ProductionLineCreate
) -> ProductionLineInDB:
    try:
        logger.info(f"Creating production line: {line_in.name}")
        
        service = ProductionLineService(db)
        
        # 检查名称是否已存在
        if service.get_by_name(line_in.name):
            logger.warning(f"Production line with name '{line_in.name}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"生产线名称 '{line_in.name}' 已存在"
            )
        
        line = service.create(line_in)
        logger.info(f"Successfully created production line: {line.name} (ID: {line.id})")
        
        return line
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating production line: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建生产线失败"
        )

@router.get("/{line_id}", response_model=ProductionLineInDB, summary="获取生产线详情")
async def read_production_line(
    *,
    db: Session = Depends(deps.get_db),
    line_id: int
) -> ProductionLineInDB:
    try:
        logger.info(f"Fetching production line with ID: {line_id}")
        
        service = ProductionLineService(db)
        line = service.get(line_id)
        
        if not line:
            logger.warning(f"Production line with ID {line_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="生产线不存在"
            )
        
        return line
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching production line {line_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取生产线详情失败"
        )

@router.put("/{line_id}", response_model=ProductionLineInDB, summary="更新生产线")
async def update_production_line(
    *,
    db: Session = Depends(deps.get_db),
    line_id: int,
    line_in: ProductionLineUpdate
) -> ProductionLineInDB:
    try:
        logger.info(f"Updating production line {line_id} with data: {line_in}")
        
        service = ProductionLineService(db)
        line = service.get(line_id)
        
        if not line:
            logger.warning(f"Production line with ID {line_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="生产线不存在"
            )
        
        # 如果更新名称，检查是否与其他生产线冲突
        if line_in.name and line_in.name != line.name:
            existing_line = service.get_by_name(line_in.name)
            if existing_line and existing_line.id != line_id:
                logger.warning(f"Production line name '{line_in.name}' conflicts with existing line {existing_line.id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"生产线名称 '{line_in.name}' 已被其他生产线使用"
                )
        
        updated_line = service.update(line, line_in)
        logger.info(f"Successfully updated production line {line_id}")
        
        return updated_line
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating production line {line_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新生产线失败"
        )

@router.delete("/{line_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除生产线")
async def delete_production_line(
    *,
    db: Session = Depends(deps.get_db),
    line_id: int
):
    try:
        logger.info(f"Deleting production line {line_id}")
        
        service = ProductionLineService(db)
        line = service.get(line_id)
        
        if not line:
            logger.warning(f"Production line with ID {line_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="生产线不存在"
            )
        
        service.delete(line_id)
        logger.info(f"Successfully deleted production line {line_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting production line {line_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除生产线失败"
        )
