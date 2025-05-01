import sys
import os
import shutil
import pytest
from fastapi.testclient import TestClient

# Ensure project root is in path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root not in sys.path:
    sys.path.insert(0, root)

import app.core.config as config_module
from app.main import app

# Create TestClient fixture
test_client = TestClient(app)

@pytest.fixture(scope="session")
def client():
    """Test client for API requests"""
    return test_client

@pytest.fixture(autouse=True)
def reset_csv(tmp_path, monkeypatch):
    """
    Before each test, write a fresh sample CSV and patch DATA_FILE_PATH
    """
    # Create a temporary CSV file with minimal valid data
    sample = tmp_path / "storage.csv"
    sample.write_text("id,region,age,seed\n1,apac,30,agtc\n2,na,25,gtac\n")

    # Patch the config constant so app reads our temp CSV
    monkeypatch.setattr(config_module, 'DATA_FILE_PATH', str(sample))

    # Create uploads directory for file upload tests
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setenv('UPLOADS_DIR', str(uploads_dir))

    yield

    # Cleanup temporary files\#
    shutil.rmtree(tmp_path)
