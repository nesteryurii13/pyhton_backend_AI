"""
Example usage script for the GPT Query API.
This script demonstrates how to interact with the API programmatically.
"""
import asyncio
import httpx
import json


async def test_api():
    """Test the GPT Query API with example queries."""
    
    base_url = "http://localhost:8000"
    
    # Test queries
    test_queries = [
        "What is the capital of France?",
        "Explain quantum computing in simple terms",
        "Write a short poem about artificial intelligence"
    ]
    
    async with httpx.AsyncClient() as client:
        print("🚀 Testing GPT Query API")
        print("=" * 50)
        
        # Test health endpoint
        try:
            health_response = await client.get(f"{base_url}/health")
            print(f"✅ Health check: {health_response.json()}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return
        
        print("\n" + "=" * 50)
        print("🤖 Testing query endpoint")
        print("=" * 50)
        
        # Test query endpoint
        for i, query in enumerate(test_queries, 1):
            try:
                print(f"\n📤 Query {i}: {query}")
                
                response = await client.post(
                    f"{base_url}/query",
                    json={"query": query},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Response: {result['response'][:100]}...")
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Request failed: {e}")
        
        print("\n" + "=" * 50)
        print("✨ API testing completed!")


def test_api_sync():
    """Synchronous version using requests (if httpx is not available)."""
    import requests
    
    base_url = "http://localhost:8000"
    
    print("🚀 Testing GPT Query API (Sync)")
    print("=" * 50)
    
    # Test health endpoint
    try:
        health_response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {health_response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test a single query
    try:
        query = "What is the meaning of life?"
        print(f"\n📤 Query: {query}")
        
        response = requests.post(
            f"{base_url}/query",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response: {result['response']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")


if __name__ == "__main__":
    print("Choose testing method:")
    print("1. Async (requires httpx)")
    print("2. Sync (requires requests)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        try:
            asyncio.run(test_api())
        except ImportError:
            print("❌ httpx not available. Install with: pip install httpx")
            print("Falling back to sync version...")
            test_api_sync()
    elif choice == "2":
        test_api_sync()
    else:
        print("Invalid choice. Running async version by default...")
        try:
            asyncio.run(test_api())
        except ImportError:
            test_api_sync()