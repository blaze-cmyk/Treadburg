"""Diagnose API Routing - See exactly what's being called"""
import asyncio
import sys
sys.path.insert(0, '.')

from open_webui.utils.unified_perplexity_service import get_unified_service

async def test_routing():
    print("\n" + "="*80)
    print("🔍 DIAGNOSING API ROUTING")
    print("="*80 + "\n")
    
    service = get_unified_service()
    
    # Check configuration
    print("📋 Configuration Check:")
    print(f"  Perplexity API Key: {'✅ Set' if service.perplexity_api_key else '❌ Missing'}")
    print(f"  OpenAI API Key: {'✅ Set' if service.openai_api_key else '❌ Missing'}")
    print()
    
    # Test 1: Text query (should use Perplexity)
    print("="*80)
    print("TEST 1: Text Query (Should use Perplexity)")
    print("="*80)
    
    query = "what is bitcoin price?"
    print(f"Query: {query}")
    print(f"Image data: None")
    print("\nCalling process_unified_query...")
    
    try:
        result = await service.process_unified_query(
            user_message=query,
            image_data=None,  # No image
            conversation_history=None,
            session_id="test_123"
        )
        
        print(f"\n✅ Result received!")
        print(f"  Success: {result.get('success')}")
        print(f"  Service used: {result.get('service_used')}")
        print(f"  Response length: {len(result.get('response', ''))}")
        
        if result.get('success'):
            content = result.get('response', '')
            print(f"\n📄 Response preview:")
            print("-"*80)
            print(content[:500])
            print("-"*80)
            
            # Check for Perplexity indicators
            has_citations = any(f"[{i}]" in content for i in range(1,6))
            has_tables = "|" in content
            
            print(f"\n🔍 Analysis:")
            print(f"  Has citations: {'✅' if has_citations else '❌'}")
            print(f"  Has tables: {'✅' if has_tables else '❌'}")
            
            if result.get('service_used') == 'perplexity_api':
                print(f"\n🎯 VERDICT: ✅ Correctly using Perplexity API!")
            else:
                print(f"\n🎯 VERDICT: ❌ Using {result.get('service_used')} instead of Perplexity!")
        else:
            print(f"\n❌ Error: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_routing())
