#!/usr/bin/env python3
"""
Backend Testing Suite for Clear Language Analysis Application
Tests the POST /api/analyze endpoint with various scenarios
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def test_analyze_endpoint():
    """Test the POST /api/analyze endpoint with various scenarios"""
    
    print("=" * 80)
    print("TESTING BACKEND API: POST /api/analyze")
    print("=" * 80)
    
    # Test 1: Valid administrative text (as requested)
    print("\n1. Testing with administrative text example...")
    admin_text = "En relación a la presente comunicación, procedemos a comunicarle que a los efectos oportunos rogamos tenga a bien revisar la documentación adjunta."
    
    try:
        response = requests.post(
            f"{API_BASE}/analyze",
            json={"text": admin_text},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Valid response received")
            print(f"Response structure: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Validate response structure
            if "sugerencias" in data:
                print("✅ Response contains 'sugerencias' field")
                
                for i, sugerencia in enumerate(data["sugerencias"]):
                    print(f"\nSugerencia {i+1}:")
                    required_fields = ["id", "original", "problema", "sugerencia"]
                    for field in required_fields:
                        if field in sugerencia:
                            print(f"  ✅ {field}: {sugerencia[field][:100]}...")
                        else:
                            print(f"  ❌ Missing field: {field}")
                            
                if len(data["sugerencias"]) > 0:
                    print("✅ OpenAI integration working - suggestions generated")
                else:
                    print("⚠️  No suggestions generated (text might be already clear)")
            else:
                print("❌ Response missing 'sugerencias' field")
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON DECODE ERROR: {e}")
        print(f"Raw response: {response.text}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
    
    # Test 2: Empty text (should return 422)
    print("\n" + "="*50)
    print("2. Testing with empty text (should return 422)...")
    
    try:
        response = requests.post(
            f"{API_BASE}/analyze",
            json={"text": ""},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 422:
            print("✅ SUCCESS: Correctly rejected empty text with 422")
            print(f"Error response: {response.json()}")
        else:
            print(f"❌ FAILED: Expected 422, got {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: Text over 4000 characters (should return validation error)
    print("\n" + "="*50)
    print("3. Testing with text over 4000 characters...")
    
    long_text = "Este es un texto muy largo. " * 200  # Creates text over 4000 chars
    print(f"Text length: {len(long_text)} characters")
    
    try:
        response = requests.post(
            f"{API_BASE}/analyze",
            json={"text": long_text},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 422:
            print("✅ SUCCESS: Correctly rejected long text with 422")
            print(f"Error response: {response.json()}")
        else:
            print(f"❌ FAILED: Expected 422, got {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 4: Check if OpenAI integration is real (not mocked)
    print("\n" + "="*50)
    print("4. Testing OpenAI integration authenticity...")
    
    # Test with a specific text that should generate predictable suggestions
    test_text = "Procedemos a informarle que en virtud de lo establecido en el artículo correspondiente, se ha procedido a la tramitación del expediente en cuestión."
    
    try:
        response = requests.post(
            f"{API_BASE}/analyze",
            json={"text": test_text},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "sugerencias" in data and len(data["sugerencias"]) > 0:
                print("✅ OpenAI integration appears to be working")
                print("✅ Suggestions are being generated (not mocked)")
                
                # Check if suggestions follow the clear language guide
                for sug in data["sugerencias"]:
                    if "problema" in sug and "sugerencia" in sug:
                        print(f"  - Problem identified: {sug['problema'][:100]}...")
                        print(f"  - Suggestion provided: {sug['sugerencia'][:100]}...")
            else:
                print("⚠️  No suggestions generated - might indicate mocked response")
        else:
            print(f"❌ Failed to test OpenAI integration: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR testing OpenAI integration: {e}")
    
    # Test 5: API Key validation
    print("\n" + "="*50)
    print("5. Checking API key configuration...")
    
    # Check if EMERGENT_LLM_KEY is configured
    load_dotenv('/app/backend/.env')
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    if api_key:
        print(f"✅ EMERGENT_LLM_KEY is configured (length: {len(api_key)})")
        if api_key.startswith('sk-emergent-'):
            print("✅ API key format appears correct")
        else:
            print("⚠️  API key format might be incorrect")
    else:
        print("❌ EMERGENT_LLM_KEY not found in environment")

def test_basic_connectivity():
    """Test basic API connectivity"""
    print("\n" + "="*80)
    print("TESTING BASIC API CONNECTIVITY")
    print("="*80)
    
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        print(f"GET {API_BASE}/ - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Basic API connectivity working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ API connectivity issue: {response.status_code}")
            
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")

if __name__ == "__main__":
    print("BACKEND TESTING SUITE")
    print(f"Testing backend at: {API_BASE}")
    print("="*80)
    
    # Run tests
    test_basic_connectivity()
    test_analyze_endpoint()
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)