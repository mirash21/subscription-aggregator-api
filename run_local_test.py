#!/usr/bin/env python3
"""
Local test script for the Subscription Service
This script demonstrates the API functionality without Docker
"""

import requests
import json
import uuid
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_create_subscription():
    """Test creating a subscription"""
    print("\nTesting subscription creation...")
    subscription_data = {
        "service_name": "Yandex Plus",
        "price": 400,
        "user_id": "60601fee-2bf1-4721-ae6f-7636e79a0cba",
        "start_date": "07-2025"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/subscriptions/", json=subscription_data)
        print(f"Create subscription: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"Created subscription ID: {data['id']}")
            return data['id']
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Create subscription failed: {e}")
        return None

def test_get_subscription(subscription_id):
    """Test getting a subscription"""
    print(f"\nTesting get subscription {subscription_id}...")
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/{subscription_id}")
        print(f"Get subscription: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Subscription data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Get subscription failed: {e}")

def test_list_subscriptions():
    """Test listing subscriptions"""
    print("\nTesting list subscriptions...")
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/")
        print(f"List subscriptions: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} subscriptions")
            for sub in data[:3]:  # Show first 3
                print(f"- {sub['service_name']} ({sub['price']} руб.)")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"List subscriptions failed: {e}")

def test_calculate_cost():
    """Test cost calculation"""
    print("\nTesting cost calculation...")
    cost_params = {
        "start_period": "01-2025",
        "end_period": "12-2025"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/cost/", params=cost_params)
        print(f"Calculate cost: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total cost: {data['total_cost']} руб.")
            print(f"Subscription count: {data['count']}")
            print(f"Period: {data['period_start']} to {data['period_end']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Calculate cost failed: {e}")

def main():
    print("=== Subscription Service Local Test ===")
    print("Make sure the service is running on localhost:8000")
    print("Start it with: uvicorn app.main:app --reload\n")
    
    # Wait a moment for user to start the service
    input("Press Enter after starting the service...")
    
    # Test health check first
    if not test_health_check():
        print("Service is not responding. Please make sure it's running.")
        return
    
    # Test CRUD operations
    subscription_id = test_create_subscription()
    
    if subscription_id:
        test_get_subscription(subscription_id)
        test_list_subscriptions()
        test_calculate_cost()
    
    print("\n=== Test Complete ===")
    print("Swagger documentation available at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()