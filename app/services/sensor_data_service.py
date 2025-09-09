from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.sensor_data import SensorData
from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.services.alarm_rule_service import AlarmRuleService
from app.services.alarm_record_service import AlarmRecordService
from app.services.export_record_service import ExportRecordService
from app.schemas.export_record import ExportRecordCreate
from app.schemas.alarm_record import AlarmRecordCreate
from app.schemas.sensor_data import SensorDataFilter, SensorDataExportFilter, SensorDataListResponse, SensorData as SensorDataSchema, UtilizationResponse
import pandas as pd
import io

logger = get_logger(__name__)


class SensorDataService:
    """传感器数据服务"""
    
    def __init__(self, db, alarm_rule_service: AlarmRuleService=None, alarm_record_service: AlarmRecordService=None, export_record_service: ExportRecordService=None):
        self.db = db
        self.alarm_rule_service = alarm_rule_service
        self.alarm_record_service = alarm_record_service
        self.export_record_service = export_record_service

    def save_sensor_data(self, sensor_data: Dict[str, Any]) -> int:
        """批量保存传感器读数到数据库"""
        try:
            data = SensorData(**sensor_data)
            self.db.add(data)
            self.db.commit()
            saved_count = 1
            
            logger.info(f"✅ Worker进程保存了 {saved_count} 条传感器数据")
            return saved_count
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"❌ 保存数据失败: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ 保存数据失败: {e}")
            raise
    

    def process_sensor_data(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理传感器数据，包括报警检查、数据转换等"""
        try:
            mutated_sensor_data = sensor_data.copy()

            self.save_sensor_data(sensor_data)

            rules = self.alarm_rule_service.get_rules_by_line(sensor_data.get('line_id'), enabled_only=True)
            rules += self.alarm_rule_service.get_rules_by_line('*', enabled_only=True)
            
            alarmed_records: List[AlarmRecordCreate] = []

            skip_params = [
                'batch_product_number', 'timestamp', 'line_id', 'component_id'
            ]

            for k, v in mutated_sensor_data.items():
                if k in skip_params:
                    continue

                newv = {
                    "value": v,
                    "alarm": False,
                    "alarmCode": "",
                    "alarmMessage": ""
                }
                for rule in rules:
                    if k.startswith(rule.parameter_name):
                        if self.alarm_rule_service.is_triggered(rule, v):
                            alarmed_records.append(AlarmRecordCreate(
                                timestamp=sensor_data.get('timestamp'),
                                line_id=sensor_data.get('line_id'),
                                parameter_name=k,
                                parameter_value=v,
                                alarm_message=self.alarm_rule_service.get_alarm_message(rule, k, v),
                                alarm_rule_id=rule.id))
                            newv["alarm"] = True
                            newv["alarmMessage"] = self.alarm_rule_service.get_alarm_message(rule, k, v)

                mutated_sensor_data[k] = newv

            for alarm_record in alarmed_records:
                self.alarm_record_service.create_alarm_record(alarm_record)

            return mutated_sensor_data
            
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")
            raise
    
    def list_sensor_data(self, filters: SensorDataFilter) -> SensorDataListResponse:
        """获取传感器数据列表（支持下采样，避免一次性返回太多点）"""
        try:
            logger.info(f"------------filters: {filters}")
            # max_points = 1000  # 控制返回的最大点数（图表友好）
            # 如果传入了时间范围，就优先做下采样
            if filters.start_time and filters.end_time:
                # 直接查询原始数据，不做下采样
                query = self.db.query(SensorData)
                
                # 添加时间范围过滤
                query = query.filter(SensorData.timestamp >= filters.start_time)
                query = query.filter(SensorData.timestamp <= filters.end_time)
                
                # 添加其他过滤条件
                if filters.line_id:
                    query = query.filter(SensorData.line_id == filters.line_id)
                if filters.component_id:
                    query = query.filter(SensorData.component_id == filters.component_id)
                
                # 按时间排序
                query = query.order_by(SensorData.timestamp)
                
                # 限制返回数量，避免一次性返回太多数据
                # query = query.limit(max_points)
                
                items = query.all()
                total = query.count()

                return SensorDataListResponse(
                    items=[SensorDataSchema.model_validate(item) for item in items],
                    total=total,
                    page=1,
                    size=len(items)
                )
            else:
                # 没有时间范围时，走原来的分页逻辑
                query = self.db.query(SensorData)
                if filters.line_id:
                    query = query.filter(SensorData.line_id == filters.line_id)
                if filters.component_id:
                    query = query.filter(SensorData.component_id == filters.component_id)
                if filters.parameter_name:
                    query = query.filter(SensorData.parameter_name == filters.parameter_name)

                total = query.count()
                skip = (filters.page - 1) * filters.size
                items = query.offset(skip).limit(filters.size).all()

                return SensorDataListResponse(
                    items=[SensorDataSchema.model_validate(item) for item in items],
                    total=total,
                    page=filters.page,
                    size=filters.size
                )

        except SQLAlchemyError as e:
            logger.error(f"Database error when listing sensor data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error listing sensor data: {e}")
            raise

    def export_sensor_data_streaming(self, filters: SensorDataExportFilter):
        """
        流式导出传感器数据，适用于大数据量场景
        生成器函数，逐块返回Excel数据
        """
        try:
            # 创建导出记录
            export_record = self.export_record_service.create_export_record(ExportRecordCreate(
                line_names=filters.line_ids,
                fields=filters.parameter_names or '',
                start_time=filters.start_time,
                end_time=filters.end_time,
            ))
            
            line_ids_list = filters.line_ids.split(',') if isinstance(filters.line_ids, str) else filters.line_ids
            parameter_names = (filters.parameter_names or '').split(',') if filters.parameter_names else []
            
            logger.info(f"开始流式导出，生产线数量: {len(line_ids_list)}")
            
            # 使用临时文件而不是内存
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                temp_path = temp_file.name
            
            total_records = 0

            # 生成Excel文件到临时文件
            with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
                
                # 首先创建一个默认的汇总表，确保至少有一个可见工作表
                summary_data = []
                
                for i, line_id in enumerate(line_ids_list):
                    logger.info(f"处理第 {i+1}/{len(line_ids_list)} 个生产线: {line_id}")
                    
                    # 查询数据
                    query = self.db.query(SensorData).filter(SensorData.line_id == line_id)
                    
                    if filters.component_id:
                        query = query.filter(SensorData.component_id == filters.component_id)
                    
                    if filters.start_time:
                        query = query.filter(SensorData.timestamp >= filters.start_time)
                    
                    if filters.end_time:
                        query = query.filter(SensorData.timestamp <= filters.end_time)
                    
                    query = query.order_by(SensorData.timestamp)
                    items = query.all()
                    
                    sheet_name = f"生产线_{line_id}"[:31]
                    
                    if items:
                        # 转换为DataFrame
                        data_list = []
                        for item in items:
                            row = {'时间戳': item.timestamp.isoformat()}
                            
                            for param_name in parameter_names:
                                if hasattr(item, param_name):
                                    value = getattr(item, param_name)
                                    row[param_name] = value
                                else:
                                    row[param_name] = None
                            
                            data_list.append(row)
                        
                        df = pd.DataFrame(data_list)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        total_records += len(items)
                        
                        # 添加到汇总表
                        summary_data.append({
                            '生产线': line_id,
                            '记录数': len(items),
                            '状态': '有数据'
                        })
                    else:
                        # 创建包含提示信息的表，确保有可见内容
                        empty_df = pd.DataFrame({
                            '时间戳': ['无数据'],
                            '提示': [f'生产线 {line_id} 在指定时间范围内无数据']
                        })
                        empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # 添加到汇总表
                        summary_data.append({
                            '生产线': line_id,
                            '记录数': 0,
                            '状态': '无数据'
                        })
                
                # 创建汇总表，确保至少有一个可见工作表
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='导出汇总', index=False)
                
                # 如果没有任何数据，创建一个额外的提示表
                if total_records == 0:
                    default_df = pd.DataFrame({
                        '提示': ['在指定条件下未找到任何数据'],
                        '查询条件': [f'生产线: {filters.line_ids}'],
                        '时间范围': [f'{filters.start_time} 到 {filters.end_time}']
                    })
                    default_df.to_excel(writer, sheet_name='查询结果', index=False)
            
            # 流式读取文件并返回
            chunk_size = 8192  # 8KB chunks
            logger.info(f"开始流式传输文件，总记录数: {total_records}")
            
            with open(temp_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
            
            logger.info(f"流式导出完成，总记录数: {total_records}")
            
        except Exception as e:
            logger.error(f"Error in streaming export: {e}")
            if 'export_record' in locals() and export_record:
                self.export_record_service.update_export_record_status_and_size(export_record.id, 'failed')
            raise
        finally:
            # 确保清理工作总是执行
            if 'export_record' in locals() and export_record:
                try:
                    logger.info(f"Updating export record {export_record.id} status to completed and size to {os.path.getsize(temp_path) if os.path.exists(temp_path) else 0}")
                    self.export_record_service.update_export_record_status_and_size(export_record.id, 'completed', os.path.getsize(temp_path) if os.path.exists(temp_path) else 0)
                except Exception as cleanup_error:
                    logger.error(f"Error updating export record: {cleanup_error}")
            
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    logger.info(f"Cleaned up temporary file: {temp_path}")
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up temporary file: {cleanup_error}")

    def get_utilization(self, filters: SensorDataFilter) -> UtilizationResponse:
        """获取设备利用率数据"""
        try:
            logger.info(f"------------filters: {filters}")
            if not filters.start_time or not filters.end_time or not filters.line_id:
                # 返回默认的空数据
                return UtilizationResponse(
                    line_id=filters.line_id or "",
                    total_run_time_seconds=0,
                    total_idle_time_seconds=0,
                    total_offline_time_seconds=0
                )

            # 计算总时间（秒）
            total_time_seconds = (filters.end_time - filters.start_time).total_seconds()
            
            # 查询运行和空闲时间
            result = self.db.query(
                func.sum(case((SensorData.motor_screw_speed > 0.1, 1), else_=0)).label("running"),
                func.sum(case((SensorData.motor_screw_speed <= 0.1, 1), else_=0)).label("idle")
            ).filter(
                SensorData.timestamp >= filters.start_time,
                SensorData.timestamp <= filters.end_time,
                SensorData.line_id == filters.line_id
            ).one()

            # 处理查询结果
            running_seconds = result.running or 0
            idle_seconds = result.idle or 0
            offline_seconds = max(0, total_time_seconds - running_seconds - idle_seconds)

            logger.info(f"------------result: running={running_seconds}, idle={idle_seconds}, offline={offline_seconds}")
            
            return UtilizationResponse(
                line_id=filters.line_id, 
                total_run_time_seconds=int(running_seconds), 
                total_idle_time_seconds=int(idle_seconds), 
                total_offline_time_seconds=int(offline_seconds)
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error when getting utilization: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting utilization: {e}")
            raise