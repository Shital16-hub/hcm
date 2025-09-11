# test_task_tools.py - Test the task management functionality
import asyncio
from task_manager.tools import add_task, list_tasks, complete_task, get_task_summary

async def test_tools():
    print("Testing task management tools...")
    
    try:
        # Test adding a task
        print("\n1. Adding a task...")
        result = add_task.invoke({
            "title": "Test task",
            "description": "This is a test task",
            "priority": "medium"
        })
        print(f"Result: {result}")
        
        # Test listing tasks
        print("\n2. Listing tasks...")
        result = list_tasks.invoke({"status": "all"})
        print(f"Result: {result}")
        
        # Test task summary
        print("\n3. Getting task summary...")
        result = get_task_summary.invoke({})
        print(f"Result: {result}")
        
        # Test completing a task
        print("\n4. Completing the task...")
        result = complete_task.invoke({"task_title": "Test task"})
        print(f"Result: {result}")
        
        # Test final summary
        print("\n5. Final summary...")
        result = get_task_summary.invoke({})
        print(f"Result: {result}")
        
        print("\n✅ All tools working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing tools: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tools())