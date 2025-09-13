# task_manager/tools_fixed.py - CORRECTED for LangGraph compatibility
import json
import os
from datetime import datetime
from typing import List, Optional
from langchain_core.tools import tool
from .models import Task
from config.settings import settings

def load_tasks() -> List[Task]:
    """Load tasks from JSON file"""
    if not os.path.exists(settings.TASKS_FILE):
        os.makedirs(os.path.dirname(settings.TASKS_FILE), exist_ok=True)
        with open(settings.TASKS_FILE, 'w') as f:
            json.dump([], f)
        return []
    
    try:
        with open(settings.TASKS_FILE, 'r') as f:
            tasks_data = json.load(f)
            return [Task(**task) for task in tasks_data]
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_tasks(tasks: List[Task]) -> None:
    """Save tasks to JSON file"""
    os.makedirs(os.path.dirname(settings.TASKS_FILE), exist_ok=True)
    
    # Convert tasks to dictionaries for JSON serialization
    tasks_data = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }
        tasks_data.append(task_dict)
    
    with open(settings.TASKS_FILE, 'w') as f:
        json.dump(tasks_data, f, indent=2)

@tool
def add_task(title: str, description: str = "", priority: str = "medium") -> str:
    """Add a new task to your task list.
    
    Args:
        title: The task title or description
        description: Optional detailed description  
        priority: Task priority (low, medium, high)
    """
    tasks = load_tasks()
    
    # Generate unique ID
    task_id = f"task_{len(tasks) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Validate priority
    if priority not in ["low", "medium", "high"]:
        priority = "medium"
    
    new_task = Task(
        id=task_id,
        title=title,
        description=description,
        priority=priority,
        created_at=datetime.now()
    )
    
    tasks.append(new_task)
    save_tasks(tasks)
    
    return f"✅ Added task: '{title}' with {priority} priority"

@tool
def list_tasks(status: str = "all") -> str:
    """List your tasks. 
    
    Args:
        status: Filter by status (all, pending, completed, in_progress)
    """
    tasks = load_tasks()
    
    if not tasks:
        return "📝 No tasks found. Say 'add task' to create your first task!"
    
    if status != "all":
        tasks = [task for task in tasks if task.status == status]
    
    if not tasks:
        return f"📝 No {status} tasks found"
    
    result = f"📋 Your tasks ({len(tasks)} total):\n\n"
    for i, task in enumerate(tasks, 1):
        status_emoji = "✅" if task.status == "completed" else "⏳" if task.status == "in_progress" else "📌"
        priority_marker = "🔴" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"
        
        result += f"{i}. {status_emoji} {priority_marker} {task.title}\n"
        if task.description:
            result += f"   💭 {task.description}\n"
    
    return result

@tool
def complete_task(task_title: str) -> str:
    """Mark a task as completed.
    
    Args:
        task_title: The title of the task to complete
    """
    tasks = load_tasks()
    
    for task in tasks:
        if task.title.lower() == task_title.lower():
            task.status = "completed"
            task.completed_at = datetime.now()
            save_tasks(tasks)
            return f"✅ Completed task: '{task.title}'"
    
    return f"❌ Task '{task_title}' not found. Try saying 'list tasks' to see available tasks."

@tool
def delete_task(task_title: str) -> str:
    """Delete a task from your list.
    
    Args:
        task_title: The title of the task to delete
    """
    tasks = load_tasks()
    
    for i, task in enumerate(tasks):
        if task.title.lower() == task_title.lower():
            removed_task = tasks.pop(i)
            save_tasks(tasks)
            return f"🗑️ Deleted task: '{removed_task.title}'"
    
    return f"❌ Task '{task_title}' not found. Try saying 'list tasks' to see available tasks."

@tool
def update_task_priority(task_title: str, priority: str) -> str:
    """Update the priority of a task.
    
    Args:
        task_title: The title of the task to update
        priority: New priority (low, medium, high)
    """
    if priority not in ["low", "medium", "high"]:
        return "❌ Priority must be 'low', 'medium', or 'high'"
    
    tasks = load_tasks()
    
    for task in tasks:
        if task.title.lower() == task_title.lower():
            task.priority = priority
            save_tasks(tasks)
            priority_emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
            return f"📝 Updated '{task.title}' priority to {priority} {priority_emoji}"
    
    return f"❌ Task '{task_title}' not found. Try saying 'list tasks' to see available tasks."

@tool
def get_task_summary() -> str:
    """Get a summary of all your tasks."""
    tasks = load_tasks()
    
    if not tasks:
        return "🎉 No tasks! You're all caught up!"
    
    pending = len([t for t in tasks if t.status == "pending"])
    in_progress = len([t for t in tasks if t.status == "in_progress"])
    completed = len([t for t in tasks if t.status == "completed"])
    
    high_priority = len([t for t in tasks if t.priority == "high" and t.status != "completed"])
    
    summary = f"📊 Task Summary:\n"
    summary += f"📌 Pending: {pending}\n"
    summary += f"⏳ In Progress: {in_progress}\n"
    summary += f"✅ Completed: {completed}\n"
    
    if high_priority > 0:
        summary += f"🔴 High Priority: {high_priority}\n"
    
    return summary