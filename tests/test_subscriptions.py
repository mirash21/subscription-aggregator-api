import pytest
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import get_db, engine, Base
from app.models.subscription import Subscription
from sqlalchemy.orm import sessionmaker

# Create test database session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override database dependency for testing
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_subscription_data():
    return {
        "service_name": "Test Service",
        "price": 500,
        "user_id": str(uuid.uuid4()),
        "start_date": "01-2025"
    }

def test_create_subscription(test_db, sample_subscription_data):
    """Test creating a new subscription"""
    response = client.post("/subscriptions/", json=sample_subscription_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["service_name"] == sample_subscription_data["service_name"]
    assert data["price"] == sample_subscription_data["price"]
    assert data["user_id"] == sample_subscription_data["user_id"]
    assert data["start_date"] == sample_subscription_data["start_date"]
    assert "id" in data

def test_get_subscription(test_db, sample_subscription_data):
    """Test getting a subscription by ID"""
    # First create a subscription
    create_response = client.post("/subscriptions/", json=sample_subscription_data)
    subscription_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/subscriptions/{subscription_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == subscription_id
    assert data["service_name"] == sample_subscription_data["service_name"]

def test_get_nonexistent_subscription(test_db):
    """Test getting a non-existent subscription"""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/subscriptions/{fake_id}")
    assert response.status_code == 404

def test_update_subscription(test_db, sample_subscription_data):
    """Test updating a subscription"""
    # First create a subscription
    create_response = client.post("/subscriptions/", json=sample_subscription_data)
    subscription_id = create_response.json()["id"]
    
    # Update it
    update_data = {
        "service_name": "Updated Service",
        "price": 700
    }
    
    response = client.put(f"/subscriptions/{subscription_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["service_name"] == "Updated Service"
    assert data["price"] == 700

def test_delete_subscription(test_db, sample_subscription_data):
    """Test deleting a subscription"""
    # First create a subscription
    create_response = client.post("/subscriptions/", json=sample_subscription_data)
    subscription_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/subscriptions/{subscription_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/subscriptions/{subscription_id}")
    assert get_response.status_code == 404

def test_list_subscriptions(test_db):
    """Test listing subscriptions"""
    response = client.get("/subscriptions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_calculate_subscription_cost(test_db):
    """Test calculating subscription cost"""
    cost_request = {
        "start_period": "01-2025",
        "end_period": "12-2025"
    }
    
    response = client.get("/subscriptions/cost/", params=cost_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "total_cost" in data
    assert "count" in data
    assert data["period_start"] == "01-2025"
    assert data["period_end"] == "12-2025"

def test_invalid_date_format():
    """Test invalid date format validation"""
    invalid_data = {
        "service_name": "Test Service",
        "price": 500,
        "user_id": str(uuid.uuid4()),
        "start_date": "invalid-date"  # Invalid format
    }
    
    response = client.post("/subscriptions/", json=invalid_data)
    assert response.status_code == 422  # Validation error

def test_negative_price():
    """Test negative price validation"""
    invalid_data = {
        "service_name": "Test Service",
        "price": -100,  # Negative price
        "user_id": str(uuid.uuid4()),
        "start_date": "01-2025"
    }
    
    response = client.post("/subscriptions/", json=invalid_data)
    assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    pytest.main([__file__, "-v"])