# test_graph.py - Test LangGraph independently
import asyncio
from task_manager.graph import create_task_manager_graph

async def test_graph():
    print("Creating LangGraph workflow...")
    try:
        graph = create_task_manager_graph()
        print("✅ Graph created successfully")
        
        # Test initial greeting (empty state)
        print("\n🧪 Testing initial greeting...")
        result = await graph.ainvoke({"messages": []})
        print("Response:", result)
        
        if result.get("messages"):
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                print(f"✅ Greeting: {last_message.content}")
            else:
                print(f"✅ Greeting: {last_message}")
        
        # Test user interaction
        print("\n🧪 Testing user interaction...")
        result = await graph.ainvoke({
            "messages": [{"role": "user", "content": "Hello"}]
        })
        
        if result.get("messages"):
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                print(f"✅ Response: {last_message.content}")
            else:
                print(f"✅ Response: {last_message}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_graph())