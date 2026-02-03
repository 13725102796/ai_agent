import requests
import json
import sys

URL = "http://127.0.0.1:8000/generate"
TOPIC = "The future of AI"

print(f"Testing Backend at {URL} with topic: '{TOPIC}'...")

try:
    response = requests.post(URL, json={"topic": TOPIC}, timeout=60)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ API Request Successful")
        
        # Check Research
        if data.get("research_data"):
            print("✅ Researcher Node: OK")
            print(f"   (Data Preview: {data['research_data'][:50]}...)")
        else:
            print("❌ Researcher Node: Failed (No data)")

        # Check Strategy
        if data.get("strategy"):
            print("✅ Strategist Node: OK")
        else:
            print("❌ Strategist Node: Failed")

        # Check Draft
        if data.get("draft"):
            print("✅ Writer Node: OK")
        else:
            print("❌ Writer Node: Failed")
            
        # Check Final
        if data.get("final_article"):
            print("✅ Editor Node: OK (Final Article Generated)")
            print("\nVerification PASSED.")
        else:
            print("❌ Editor Node: Failed")
            
    else:
        print(f"\n❌ API Request Failed with Code {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"\n❌ Connection Failed: {e}")
    print("Is the backend running?")
