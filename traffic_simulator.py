import requests
import random
import time

BASE_URL = "http://localhost:8000"

def simulate_traffic():
    while True:
        item_id = random.randint(1, 100)
        url = f"{BASE_URL}/items/{item_id}"
        try:
            r = requests.get(url, timeout=5)
            print(f"{r.status_code} -> {url}")
        except Exception as e:
            print("Request error:", e)
        time.sleep(random.uniform(0.1, 0.5))

if __name__ == "__main__":
    simulate_traffic()





























'''import requests
import random
import time

BASE_URL = "http://localhost:8000"

def simulate_traffic():
    while True:
        try:
            item_id = random.randint(1, 100)
            url = f"{BASE_URL}/items/{item_id}"
            
            print(f"Sending request to {url}")
            response = requests.get(url)
            
            if response.status_code == 200:
                print(f"Success! Response: {response.json()}")
            else:
                print(f"Error: {response.status_code}, {response.text}")
                
            time.sleep(random.uniform(0.1, 0.5))
            
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}. Is the FastAPI service running?")
            time.sleep(2)

if __name__ == "__main__":
    simulate_traffic()

'''
