import requests
import json
from datetime import datetime

URL = "http://localhost:8000/analyze"
HEADERS = {"x-api-key": "honeytrap_9XfT2AqP_2026", "Content-Type": "application/json"}

def test_scam_message():
    print("\n--- Testing Scam Message ---")
    payload = {
        "sessionId": "test-session-123",
        "message": {
            "sender": "scammer",
            "text": "URGENT: Your connection will be cut off tonight. Pay immediately to this UPI: scam@upi",
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS"}
    }
    
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        print(f"Status: {response.status_code}")
        print("Response:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Failed to connect: {e}")

def test_normal_message():
    print("\n--- Testing Normal Message ---")
    payload = {
        "sessionId": "test-session-456",
        "message": {
            "sender": "user",
            "text": "Hi, how are you?",
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS"}
    }
    
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        print(f"Status: {response.status_code}")
        print("Response:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_scam_message()
    test_normal_message()
