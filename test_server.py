#!/usr/bin/env python3
"""
Скрипт для тестирования сервера EVE Profit Master
"""
import requests
import json

def test_server():
    base_url = "https://eve-profitmaster.onrender.com"
    
    print("Testing EVE Profit Master Backend...")
    print("=" * 50)
    
    # Тест 1: Проверка доступности
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"✅ Server is running: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Server is not accessible: {e}")
        return
    
    # Тест 2: Проверка CORS
    try:
        headers = {
            'Origin': 'https://eve-profitmaster-1.onrender.com',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{base_url}/cors-test", headers=headers, timeout=10)
        print(f"✅ CORS preflight: {response.status_code}")
        print(f"CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
    
    # Тест 3: Проверка health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Health data: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Тест 4: Проверка CORS test endpoint
    try:
        headers = {'Origin': 'https://eve-profitmaster-1.onrender.com'}
        response = requests.get(f"{base_url}/cors-test", headers=headers, timeout=10)
        print(f"✅ CORS test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"CORS test data: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
    
    # Тест 5: Проверка get_characters endpoint
    try:
        headers = {'Origin': 'https://eve-profitmaster-1.onrender.com'}
        response = requests.get(f"{base_url}/get_characters", headers=headers, timeout=10)
        print(f"✅ Get characters: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Characters count: {len(data)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"❌ Get characters failed: {e}")

if __name__ == "__main__":
    test_server()
