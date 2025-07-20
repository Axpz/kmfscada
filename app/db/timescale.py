"""
TimescaleDB initialization and management module
"""
from sqlalchemy import text
from app.core.database import engine
from app.core.logging import get_logger

logger = get_logger(__name__)

def init() -> None:
    create_extensions()
    create_hypertable("sensor_readings")


def create_extensions() -> None:
    """
    Initialize TimescaleDB extensions and hypertables
    
    Args:
        tables: List of existing table names
    """
    with engine.connect() as conn:
        logger.info("Initializing TimescaleDB...")
        
        # 创建 TimescaleDB 扩展
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
        logger.info("TimescaleDB extension created/verified")
        
        # 检查 TimescaleDB 扩展状态
        result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'timescaledb'"))
        if result.fetchone():
            logger.info("TimescaleDB extension is active")
        else:
            logger.warning("TimescaleDB extension not found")
        
        # 创建 timeseries schema
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS timeseries"))
        logger.info("Timeseries schema created/verified")
        
        # 检查 timeseries schema
        result = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'timeseries'"))
        if result.fetchone():
            logger.info("Timeseries schema exists")
        else:
            logger.warning("Timeseries schema not found")
        
        conn.commit()
        logger.info("TimescaleDB initialization completed")


def get_hypertable_info() -> dict:
    """
    Get information about TimescaleDB hypertables
    
    Returns:
        dict: Information about hypertables, dimensions, and chunks
    """

    try:
        with engine.connect() as conn:
            # Get hypertables
            result = conn.execute(text("SELECT * FROM timescaledb_information.hypertables"))
            hypertables = [dict(row._mapping) for row in result]
            
            # Get dimensions
            result = conn.execute(text("SELECT * FROM timescaledb_information.dimensions"))
            dimensions = [dict(row._mapping) for row in result]
            
            # Get chunks
            result = conn.execute(text("SELECT * FROM timescaledb_information.chunks"))
            chunks = [dict(row._mapping) for row in result]
            
            return {
                "hypertables": hypertables,
                "dimensions": dimensions,
                "chunks": chunks
            }
    except Exception as e:
        logger.error(f"Failed to get TimescaleDB info: {e}")
        return {"error": str(e)}


def create_hypertable(table_name: str, time_column: str = "timestamp", chunk_interval: str = "1 day") -> bool:
    """
    Create a new hypertable
    
    Args:
        table_name: Name of the table to convert to hypertable
        time_column: Name of the time column
        chunk_interval: Chunk time interval
        
    Returns:
        bool: True if successful, False otherwise
    """
    
    try:
        with engine.connect() as conn:
            # Create hypertable
            conn.execute(text(f"SELECT create_hypertable('public.{table_name}', '{time_column}', if_not_exists => TRUE, migrate_data => TRUE)"))
            logger.info(f"Hypertable created for {table_name}")
            
            # Set chunk time interval
            conn.execute(text(f"SELECT set_chunk_time_interval('public.{table_name}', INTERVAL '{chunk_interval}')"))
            logger.info(f"Chunk time interval set to {chunk_interval} for {table_name}")
            
            conn.commit()
            return True
            
    except Exception as e:
        logger.error(f"Failed to create hypertable for {table_name}: {e}")
        return False
