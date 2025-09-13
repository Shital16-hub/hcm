import os
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")

def test_elevenlabs_api():
    """Test ElevenLabs API independently"""
    api_key = os.getenv('ELEVEN_API_KEY')
    
    if not api_key:
        print("❌ No ELEVEN_API_KEY found")
        return False
        
    # Test API connectivity
    headers = {"xi-api-key": api_key}
    
    try:
        # Test voices endpoint
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices", 
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ ElevenLabs API Key Valid")
            voices = response.json()
            print(f"✅ Found {len(voices.get('voices', []))} voices")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    test_elevenlabs_api()
