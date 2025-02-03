from dotenv import load_dotenv
import pytest

from app import db_config
from app.constant import set_env_name

@pytest.fixture(scope="session")
def db_connection():
    """Start Test database"""
    load_dotenv()
    set_env_name('test')
    conn = db_config()

    yield conn

    conn.close()
