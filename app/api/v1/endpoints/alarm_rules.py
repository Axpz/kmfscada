from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.api import deps
from app.services.alarm_rule_service import AlarmRuleService
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=schemas.AlarmRuleList)
def read_alarm_rules(
    db: Session = Depends(deps.get_db),
    page: int = 1,
    size: int = 100,
) -> Any:
    """
    获取所有报警规则
    """
    service = AlarmRuleService(db)
    rules = service.get_all_rules(skip=(page-1)*size, limit=size)
    total = service.get_rules_count()
    
    return {
        "items": rules,
        "total": total,
        "page": page,  # 计算当前页码
        "size": size
    }


@router.post("/", response_model=schemas.AlarmRule)
def create_alarm_rule(
    *,
    db: Session = Depends(deps.get_db),
    alarm_rule_in: schemas.AlarmRuleCreate,
) -> Any:
    """
    创建新的报警规则
    """
    service = AlarmRuleService(db)
    
    # 检查规则是否已存在
    existing_rules = service.get_rules_by_line(alarm_rule_in.line_id, False)
    logger.info(f"Existing rules: {existing_rules}")
    for rule in existing_rules:
        if rule.parameter_name == alarm_rule_in.parameter_name:
            logger.warning(f"生产线 {alarm_rule_in.line_id} 的参数 {alarm_rule_in.parameter_name} 已存在规则")
            raise HTTPException(
                status_code=400,
                detail=f"生产线 {alarm_rule_in.line_id} 的参数 {alarm_rule_in.parameter_name} 已存在规则"
            )
    logger.info(f"Creating alarm rule: {alarm_rule_in.dict()}")
    
    return service.create_rule(alarm_rule_in.dict())


@router.put("/{alarm_rule_id}", response_model=schemas.AlarmRule)
def update_alarm_rule(
    *,
    db: Session = Depends(deps.get_db),
    alarm_rule_id: int,
    alarm_rule_in: schemas.AlarmRuleUpdate,
) -> Any:
    """
    更新报警规则
    """
    service = AlarmRuleService(db)
    
    # 检查规则是否存在
    rule = service.get_rules_by_id(alarm_rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="报警规则不存在")
    
    # 更新规则
    updated_rule = service.update_rule(alarm_rule_id, alarm_rule_in.dict(exclude_unset=True))
    return updated_rule


@router.delete("/{alarm_rule_id}")
def delete_alarm_rule(
    *,
    db: Session = Depends(deps.get_db),
    alarm_rule_id: int,
) -> Any:
    """
    删除报警规则
    """
    service = AlarmRuleService(db)
    
    # 检查规则是否存在
    rule = service.get_rules_by_id(alarm_rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="报警规则不存在")
    
    # 删除规则
    success = service.delete_rule(alarm_rule_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除失败")
    
    return {"message": "删除成功"}


@router.get("/parameters", response_model=List[str])
def get_available_parameters() -> Any:
    """
    获取可用的监控参数列表
    """
    # 返回前端定义的参数列表
    return [
        "current_length", "diameter", "fluoride_concentration",
        "temp_body", "temp_flange", "temp_mold",
        "current_body", "current_flange", "current_mold",
        "motor_screw_speed", "motor_screw_torque", "motor_current",
        "motor_traction_speed", "motor_vacuum_speed",
        "winder_speed", "winder_torque", "winder_layer_count",
        "winder_tube_speed", "winder_tube_count"
    ]


@router.get("/lines", response_model=List[str])
def get_available_lines() -> Any:
    """
    获取可用的监控参数列表
    """
    # 返回前端定义的参数列表
    return [
        "*", "1", "2", "3", "4", "5", "6", "7", "8",
    ]
