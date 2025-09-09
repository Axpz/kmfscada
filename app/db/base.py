# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.sensor_data import SensorData  # noqa
from app.models.production_line import ProductionLine  # noqa

# Import TimescaleDB functions
from app.db.timescale import init as tc_init, create_hypertable, get_hypertable_info
from app.core.logging import get_logger

logger = get_logger(__name__)


# Database initialization function
def db_init() -> bool:
    try:
        logger.info("Initializing TimescaleDB...")
        tc_init()
        logger.info("Creating hypertable...")
        create_hypertable("sensor_data")
        logger.info("Getting hypertable info...")
        logger.info(get_hypertable_info())
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

