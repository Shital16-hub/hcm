from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Simple in-memory task storage
TASKS = []

def add_todo(task: str) -> str:
    """Add a new task."""
    global TASKS
    todo_id = len(TASKS) + 1
    new_todo = {"id": todo_id, "task": task, "completed": False}
    TASKS.append(new_todo)
    logger.info(f"✅ Added task #{todo_id}: {task}")
    return f"Added task #{todo_id}: {task}"

def list_todos() -> str:
    """List all tasks."""
    global TASKS
    if not TASKS:
        return "You have no tasks. Say 'add task' followed by your task description."
    
    if len(TASKS) == 1:
        task = TASKS[0]
        status = "done" if task["completed"] else "pending"
        return f"You have 1 task: {task['task']} - {status}"
    
    pending = [t for t in TASKS if not t["completed"]]
    completed = [t for t in TASKS if t["completed"]]
    
    summary = f"You have {len(TASKS)} tasks"
    if pending:
        summary += f", {len(pending)} pending"
    if completed:
        summary += f", {len(completed)} completed"
    
    # List first 2 pending tasks for brevity
    if pending:
        task_list = ". ".join([f"Task {t['id']}: {t['task']}" for t in pending[:2]])
        summary += f". Pending: {task_list}"
    
    return summary

def complete_todo(todo_id: int) -> str:
    """Complete a task."""
    global TASKS
    for task in TASKS:
        if task["id"] == todo_id:
            if task["completed"]:
                return f"Task #{todo_id} is already done"
            task["completed"] = True
            return f"Completed: {task['task']}"
    return f"Task #{todo_id} not found"

def delete_todo(todo_id: int) -> str:
    """Delete a task."""
    global TASKS
    for i, task in enumerate(TASKS):
        if task["id"] == todo_id:
            removed = TASKS.pop(i)
            return f"Deleted: {removed['task']}"
    return f"Task #{todo_id} not found"

def create_task_manager_graph():
    """Create optimized ReAct agent."""
    return create_react_agent(
        model=ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.2,        # More consistent responses
            max_tokens=40,          # Shorter responses
            timeout=10.0            # Faster timeout
        ),
        tools=[add_todo, list_todos, complete_todo, delete_todo],
        prompt="""You are a voice task manager. Keep responses under 15 words for smooth voice interaction.

COMMANDS:
- "add task [description]" → use add_todo
- "list tasks" → use list_todos  
- "complete task [number]" → use complete_todo
- "delete task [number]" → use delete_todo

RULES:
- Be brief and natural
- Always use appropriate tools
- For greetings, be welcoming but brief
- For unclear requests, ask for clarification

Examples:
- "add task buy milk" → add_todo("buy milk") → "Added task #1: buy milk"  
- "list tasks" → list_todos() → [brief summary]
- "hello" → "Hi! Try 'add task' or 'list tasks'"
"""
    )
