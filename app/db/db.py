import logging
import subprocess

from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import Session

from app.config import ConfigDatabase
from app.db.session import DbSession

logger = logging.getLogger(__name__)


class Database:
    _SQLITE_PREFIX = "sqlite://"

    def __init__(self, config: ConfigDatabase):
        try:
            if self._SQLITE_PREFIX in config.dsn:
                self.engine = create_engine(
                    config.dsn,
                    connect_args={"check_same_thread": False},
                    # This + static pool is needed for sqlite in-memory tables
                    poolclass=StaticPool,
                )
            else:
                self.engine = create_engine(
                    config.dsn,
                    echo=False,
                    pool_pre_ping=config.pool_pre_ping,
                    pool_recycle=config.pool_recycle,
                    pool_size=config.pool_size,
                    max_overflow=config.max_overflow,
                )
        except BaseException as e:
            logger.error("Error while connecting to database: %s", e)
            raise e

        if config.create_tables:
            self.generate_tables()

    @staticmethod
    def generate_tables() -> None:
        # TODO: Only for testing purposes
        logger.info("Generating tables...")
        migrate_command = "tools/./migrate_db.sh addressing_db postgres postgres testing"
        out = subprocess.run(migrate_command.split(), capture_output=True)
        logger.info(out.stdout.decode("utf-8"))

    def truncate_tables(self) -> None:
        tables = [
            "organization_affiliations",
            "endpoints",
            "organizations",
            "healthcare_services",
            "locations",
            "practitioners",
            "practitioner_roles",
        ]

        with self.get_db_session() as session:
            session.execute(text("TRUNCATE TABLE " + ", ".join(tables)))
            session.commit()

    def is_healthy(self) -> bool:
        """
        Check if the database is healthy

        :return: True if the database is healthy, False otherwise
        """
        try:
            with Session(self.engine) as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.info("Database is not healthy: %s", e)
            return False

    def get_db_session(self) -> DbSession:
        return DbSession(self.engine)
