#!/usr/bin/env python3
"""
Quick test to verify the performance endpoint is working correctly.
"""
import requests
import json

def test_performance_endpoint():
    """Test the performance data endpoint."""
    base_url = "http://localhost:5000"
    endpoint = "/rag/performance_data"
    
    periods = ["7d", "30d", "90d"]
    
    for period in periods:
        print(f"\n=== Testing period: {period} ===")
        url = f"{base_url}{endpoint}?period={period}"
        
        try:
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("Response Data:")
                print(json.dumps(data, indent=2))
                
                # Validate expected structure
                required_keys = ["success", "labels", "query_counts", "relevance_scores"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    print(f"❌ Missing keys: {missing_keys}")
                else:
                    print("✅ All required keys present")
                    
                    # Check data consistency
                    if len(data["labels"]) == len(data["query_counts"]) == len(data["relevance_scores"]):
                        print("✅ Data arrays have consistent lengths")
                    else:
                        print("❌ Data arrays have inconsistent lengths")
                        print(f"Labels: {len(data['labels'])}, Query counts: {len(data['query_counts'])}, Relevance scores: {len(data['relevance_scores'])}")
            else:
                print(f"❌ Error response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode failed: {e}")
            print(f"Raw response: {response.text}")

if __name__ == "__main__":
    test_performance_endpoint()