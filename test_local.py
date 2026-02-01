import requests
import json
from datetime import datetime

URL = "http://localhost:8000/analyze"
HEADERS = {"x-api-key": "honeytrap_9XfT2AqP_2026", "Content-Type": "application/json"}

def test_problem_statement_example():
    """Test with the exact example from problem statement"""
    print("\n=== Testing Problem Statement Example ===")
    
    # First message
    payload = {
        "sessionId": "test-session-ps",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately.",
            "timestamp": "2026-01-21T10:15:30Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        print(f"Status: {response.status_code}")
        result = response.json()
        print("Response:", json.dumps(result, indent=2))
        print(f"Agent Reply: {result.get('reply', 'N/A')}")
    except Exception as e:
        print(f"Failed: {e}")

def test_multi_turn_conversation():
    """Test multi-turn conversation to trigger callback"""
    print("\n=== Testing Multi-Turn Conversation (5+ messages) ===")
    
    session_id = "test-session-multiturn"
    conversation_history = []
    
    scam_messages = [
        "Your bank account will be blocked. Verify now!",
        "Share your UPI ID to avoid suspension.",
        "We need your account number for verification.",
        "Send OTP received on your phone.",
        "Transfer Rs. 100 to this UPI: scammer@upi to activate.",
        "Final warning! Account will be closed in 1 hour."
    ]
    
    for i, scam_msg in enumerate(scam_messages, 1):
        print(f"\n--- Message {i} ---")
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": scam_msg,
                "timestamp": datetime.now().isoformat()
            },
            "conversationHistory": conversation_history.copy()
        }
        
        try:
            response = requests.post(URL, json=payload, headers=HEADERS)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Agent Reply: {result.get('reply', 'N/A')}")
            
            # Update conversation history
            conversation_history.append({
                "sender": "scammer",
                "text": scam_msg,
                "timestamp": datetime.now().isoformat()
            })
            conversation_history.append({
                "sender": "user",
                "text": result.get('reply', ''),
                "timestamp": datetime.now().isoformat()
            })
            
            if i == 5:
                print("\n⚠️  Callback should be triggered after this message!")
                
        except Exception as e:
            print(f"Failed: {e}")
            break

def test_minimal_payload():
    """Test with minimal/empty payload"""
    print("\n=== Testing Minimal Payload ===")
    payload = {"sessionId": "test-empty"}
    
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        print(f"Status: {response.status_code}")
        result = response.json()
        print("Response:", json.dumps(result, indent=2))
    except Exception as e:
        print(f"Failed: {e}")

def test_normal_message():
    """Test with normal non-scam message"""
    print("\n=== Testing Normal Message ===")
    payload = {
        "sessionId": "test-normal",
        "message": {
            "sender": "user",
            "text": "Hi, how are you?",
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": []
    }
    
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        print(f"Status: {response.status_code}")
        result = response.json()
        print("Response:", json.dumps(result, indent=2))
        print(f"Agent Reply: {result.get('reply', 'N/A')}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("HONEYPOT API TESTING")
    print("=" * 60)
    
    test_minimal_payload()
    test_problem_statement_example()
    test_normal_message()
    test_multi_turn_conversation()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
