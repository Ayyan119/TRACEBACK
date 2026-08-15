import os
from alembic.config import Config
from app.core.config import settings


def test_alembic_config_load():
    """Verify that alembic.ini loads properly and reads settings.DATABASE_URL."""
    alembic_cfg_path = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
    assert os.path.exists(alembic_cfg_path)

    alembic_cfg = Config(alembic_cfg_path)
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    url = alembic_cfg.get_main_option("sqlalchemy.url")
    assert url == settings.DATABASE_URL
