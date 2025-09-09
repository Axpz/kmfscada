from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.alarm_rule import AlarmRule
from app.schemas.alarm_record import AlarmRecordCreate
from app.core.logging import get_logger

logger = get_logger(__name__)


class AlarmRuleService:
    """报警规则服务 - 处理报警规则的业务逻辑"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def is_triggered(self, rule: AlarmRule, value: float) -> bool:
        """检查给定值是否触发报警规则"""
        if not rule.is_enabled:
            return False
        
        # 检查下限
        if rule.lower_limit is not None and value < rule.lower_limit:
            return True
        
        # 检查上限
        if rule.upper_limit is not None and value > rule.upper_limit:
            return True
        
        return False
    
    def get_alarm_message(self, rule: AlarmRule, key: str, value: float) -> str:
        """获取报警消息"""
        if not self.is_triggered(rule, value):
            return ""
        
        if rule.lower_limit is not None and value < rule.lower_limit:
            return f"{key} 值 {value} 低于下限 {rule.lower_limit}"
        elif rule.upper_limit is not None and value > rule.upper_limit:
            return f"{key} 值 {value} 高于上限 {rule.upper_limit}"
        
        return f"{key} 值 {value} 超出范围"
    
    def get_parameter_names(self) -> list:
        """获取所有可用的参数名称"""
        return [
            # 生产业务数据
            "current_length", "target_length", "diameter", "fluoride_concentration",
            # 温度传感器组
            "temp_body_zone1", "temp_body_zone2", "temp_body_zone3", "temp_body_zone4",
            "temp_flange_zone1", "temp_flange_zone2", "temp_mold_zone1", "temp_mold_zone2",
            # 电流传感器组
            "current_body_zone1", "current_body_zone2", "current_body_zone3", "current_body_zone4",
            "current_flange_zone1", "current_flange_zone2", "current_mold_zone1", "current_mold_zone2",
            # 电机参数
            "motor_screw_speed", "motor_screw_torque", "motor_current", 
            "motor_traction_speed", "motor_vacuum_speed",
            # 收卷机
            "winder_speed", "winder_torque", "winder_layer_count", 
            "winder_tube_speed", "winder_tube_count",
        ]
    
    def get_rules_by_id(self, id: int) -> Optional[AlarmRule]:
        """根据ID获取规则"""
        return self.db.query(AlarmRule).filter(AlarmRule.id == id).first()
    
    def get_rules_by_line(self, line_id: str, enabled_only: bool = True) -> List[AlarmRule]:
        """获取指定生产线的规则"""
        query = self.db.query(AlarmRule).filter(AlarmRule.line_id == line_id)
        if enabled_only:
            query = query.filter(AlarmRule.is_enabled == True)
        return query.all()
    
    def get_all_rules(self, skip: int = 0, limit: int = 100) -> List[AlarmRule]:
        """获取所有规则，支持分页"""
        return self.db.query(AlarmRule).offset(skip).limit(limit).all()
    
    def get_rules_count(self) -> int:
        """获取规则总数"""
        return self.db.query(AlarmRule).count()
    
    def create_rule(self, rule_data: Dict[str, Any]) -> AlarmRule:
        """创建新规则"""
        try:
            rule = AlarmRule(**rule_data)
            self.db.add(rule)
            self.db.commit()
            self.db.refresh(rule)
            
            logger.info(f"创建报警规则: {rule.line_id}/{rule.parameter_name}")
            return rule
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建报警规则失败: {e}")
            raise
    
    def update_rule(self, rule_id: int, updates: Dict[str, Any]) -> Optional[AlarmRule]:
        """更新规则"""
        try:
            rule = self.db.query(AlarmRule).filter(AlarmRule.id == rule_id).first()
            if not rule:
                logger.warning(f"规则不存在: {rule_id}")
                return None
            
            # 更新字段
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            self.db.commit()
            self.db.refresh(rule)
            
            logger.info(f"更新报警规则: {rule.line_id}/{rule.parameter_name}")
            return rule
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新报警规则失败: {e}")
            raise
    
    def delete_rule(self, rule_id: int) -> bool:
        """删除规则"""
        try:
            rule = self.db.query(AlarmRule).filter(AlarmRule.id == rule_id).first()
            if not rule:
                logger.warning(f"规则不存在: {rule_id}")
                return False
            
            self.db.delete(rule)
            self.db.commit()
            
            logger.info(f"删除报警规则: {rule.line_id}/{rule.parameter_name}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除报警规则失败: {e}")
            raise
    
    def enable_rule(self, rule_id: int) -> bool:
        """启用规则"""
        return self.update_rule(rule_id, {"is_enabled": True}) is not None
    
    def disable_rule(self, rule_id: int) -> bool:
        """禁用规则"""
        return self.update_rule(rule_id, {"is_enabled": False}) is not None
    
    def check_sensor_data_alarms(self, sensor_data: Dict[str, Any], line_id: str) -> List[AlarmRecordCreate]:
        """检查传感器数据的报警"""
        try:
            # 获取该生产线的所有启用规则
            rules = self.get_rules_by_line(line_id, enabled_only=True)
            rules += self.get_rules_by_line('*', enabled_only=True)

            
            triggered_alarms: List[Tuple[str, AlarmRecordCreate]] = []
            for rule in rules:
                # 获取参数值
                values = { attr_name: sensor_data.get(attr_name) for attr_name in sensor_data if attr_name.startswith(rule.parameter_name) }
                for attr_name, value in values.items():
                    if value is not None and self.is_triggered(rule, value):
                        alarm_record = AlarmRecordCreate(
                            alarm_rule_id=rule.id,
                            parameter_name=attr_name,
                            parameter_value=value,
                            alarm_message=self.get_alarm_message(rule, value),
                            timestamp=sensor_data.timestamp,
                            line_id=sensor_data.line_id
                        )
                        triggered_alarms.append((attr_name, alarm_record))
                
            return triggered_alarms
            
        except Exception as e:
            logger.error(f"检查传感器数据报警失败: {e}")
            return []
