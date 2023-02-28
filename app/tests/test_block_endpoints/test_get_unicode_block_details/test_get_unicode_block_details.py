from fastapi.testclient import TestClient

from app.main import app
from app.tests.test_block_endpoints.test_get_unicode_block_details.data import BLOCK_ETHIOPIC_EXTENDED_A, BLOCK_HEBREW

client = TestClient(app)


def test_get_block_hebrew():
    response = client.get("v1/blocks/HEBREW")
    assert response.status_code == 200
    assert response.json() == BLOCK_HEBREW


def test_get_ethiopic_extended_a():
    response = client.get("v1/blocks/ETHIOPIC_EXTENDED_A")
    assert response.status_code == 200
    assert response.json() == BLOCK_ETHIOPIC_EXTENDED_A
