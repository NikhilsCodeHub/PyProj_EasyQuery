"""
Enhanced script to test different rate limiting strategies
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_ip_based_rate_limit():
    """Test IP-based rate limiting on the QnA endpoint"""
    print("Testing IP-based rate limiting on /api/v2/qna endpoint...")
    
    # Test data
    test_question = {"question": "What is the total sales?"}
    
    success_count = 0
    rate_limited_count = 0
    
    # Make requests to test rate limiting
    for i in range(15):  # Try 15 requests
        try:
            response = requests.post(
                f"{BASE_URL}/api/v2/qna",
                json=test_question,
                timeout=5
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"Request {i+1}: SUCCESS")
            elif response.status_code == 429:  # Rate limited
                rate_limited_count += 1
                print(f"Request {i+1}: RATE LIMITED")
                print(f"  Headers: {dict(response.headers)}")
            else:
                print(f"Request {i+1}: ERROR {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request {i+1}: CONNECTION ERROR - {e}")
        
        time.sleep(1)  # Wait 1 second between requests
    
    print(f"\nIP-based rate limiting results:")
    print(f"Successful requests: {success_count}")
    print(f"Rate limited requests: {rate_limited_count}")
    print(f"Total requests: {success_count + rate_limited_count}")

def test_global_rate_limit():
    """Test global rate limiting (simulating multiple users)"""
    print("\nTesting global rate limiting (simulating multiple users)...")
    
    test_question = {"question": "What is the total sales?"}
    
    # Simulate different users with different headers
    users = [
        {"user-id": "user1", "x-api-key": "key1"},
        {"user-id": "user2", "x-api-key": "key2"},
        {"user-id": "user3", "x-api-key": "key3"}
    ]
    
    total_success = 0
    total_rate_limited = 0
    
    for user_idx, headers in enumerate(users):
        print(f"\n--- Testing with User {user_idx + 1} ---")
        success_count = 0
        rate_limited_count = 0
        
        for i in range(5):  # 5 requests per user
            try:
                response = requests.post(
                    f"{BASE_URL}/api/v2/qna",
                    json=test_question,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"User {user_idx + 1} Request {i+1}: SUCCESS")
                elif response.status_code == 429:
                    rate_limited_count += 1
                    print(f"User {user_idx + 1} Request {i+1}: RATE LIMITED")
                else:
                    print(f"User {user_idx + 1} Request {i+1}: ERROR {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"User {user_idx + 1} Request {i+1}: CONNECTION ERROR - {e}")
            
            time.sleep(0.5)  # Shorter delay for global testing
        
        total_success += success_count
        total_rate_limited += rate_limited_count
        print(f"User {user_idx + 1} - Success: {success_count}, Rate Limited: {rate_limited_count}")
    
    print(f"\nGlobal rate limiting results:")
    print(f"Total successful requests: {total_success}")
    print(f"Total rate limited requests: {total_rate_limited}")

def test_user_based_rate_limit():
    """Test user-based rate limiting"""
    print("\nTesting user-based rate limiting...")
    
    test_question = {"question": "What is the total sales?"}
    
    # Test with specific user ID
    headers = {"user-id": "test-user-123"}
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(25):  # Try 25 requests for one user
        try:
            response = requests.post(
                f"{BASE_URL}/api/v2/qna",
                json=test_question,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                success_count += 1
                if i % 5 == 0:  # Print every 5th request
                    print(f"Request {i+1}: SUCCESS")
            elif response.status_code == 429:
                rate_limited_count += 1
                print(f"Request {i+1}: RATE LIMITED")
            else:
                print(f"Request {i+1}: ERROR {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request {i+1}: CONNECTION ERROR - {e}")
        
        time.sleep(0.5)
    
    print(f"\nUser-based rate limiting results:")
    print(f"Successful requests: {success_count}")
    print(f"Rate limited requests: {rate_limited_count}")

def test_api_key_rate_limit():
    """Test API key-based rate limiting"""
    print("\nTesting API key-based rate limiting...")
    
    test_question = {"question": "What is the total sales?"}
    
    # Test with specific API key
    headers = {"x-api-key": "test-api-key-456"}
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(55):  # Try 55 requests for one API key
        try:
            response = requests.post(
                f"{BASE_URL}/api/v2/qna",
                json=test_question,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                success_count += 1
                if i % 10 == 0:  # Print every 10th request
                    print(f"Request {i+1}: SUCCESS")
            elif response.status_code == 429:
                rate_limited_count += 1
                print(f"Request {i+1}: RATE LIMITED")
            else:
                print(f"Request {i+1}: ERROR {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request {i+1}: CONNECTION ERROR - {e}")
        
        time.sleep(0.2)
    
    print(f"\nAPI key-based rate limiting results:")
    print(f"Successful requests: {success_count}")
    print(f"Rate limited requests: {rate_limited_count}")

def test_health_endpoint():
    """Test rate limiting on health endpoint"""
    print("\nTesting rate limiting on /api/v1/health endpoint...")
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(35):  # Try 35 requests
        try:
            response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
            
            if response.status_code == 200:
                success_count += 1
                if i % 10 == 0:  # Print every 10th request
                    print(f"Request {i+1}: SUCCESS")
            elif response.status_code == 429:
                rate_limited_count += 1
                print(f"Request {i+1}: RATE LIMITED")
            else:
                print(f"Request {i+1}: ERROR {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request {i+1}: CONNECTION ERROR - {e}")
            break
    
    print(f"\nHealth endpoint results:")
    print(f"Successful requests: {success_count}")
    print(f"Rate limited requests: {rate_limited_count}")

def get_current_strategy():
    """Get the current rate limiting strategy from the server"""
    try:
        # This would require adding an endpoint to return current config
        # For now, we'll just indicate it should be checked manually
        print("Current rate limiting strategy: Check service/rate_limit_config.py")
        print("Available strategies: ip, global, user_id, api_key, combined, endpoint_specific")
    except:
        pass

if __name__ == "__main__":
    print("Enhanced Rate Limiting Test Script")
    print("=" * 50)
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("You can start it with: uvicorn service.api_main:app --reload")
    print()
    
    get_current_strategy()
    print()
    
    print("Available tests:")
    print("1. IP-based rate limiting (default)")
    print("2. Global rate limiting simulation")
    print("3. User-based rate limiting")
    print("4. API key-based rate limiting")
    print("5. Health endpoint rate limiting")
    print("6. Run all tests")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        test_ip_based_rate_limit()
    elif choice == "2":
        test_global_rate_limit()
    elif choice == "3":
        test_user_based_rate_limit()
    elif choice == "4":
        test_api_key_rate_limit()
    elif choice == "5":
        test_health_endpoint()
    elif choice == "6":
        test_ip_based_rate_limit()
        test_global_rate_limit()
        test_user_based_rate_limit()
        test_api_key_rate_limit()
        test_health_endpoint()
    else:
        print("Invalid choice. Running IP-based test...")
        test_ip_based_rate_limit()
