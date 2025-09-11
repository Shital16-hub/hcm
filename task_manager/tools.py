# task_manager/tools.py - FIXED for Pydantic compatibility
import json
import os
from datetime import datetime
from typing import List, Optional
from langchain_core.tools import tool
from .models import Task, TaskManagerState
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
    """Save tasks to JSON file - FIXED for Pydantic compatibility"""
    os.makedirs(os.path.dirname(settings.TASKS_FILE), exist_ok=True)
    
    # Convert tasks to dictionaries manually
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
def add_task(title: str, description: str = "", priority: str = "medium", due_date: str = None) -> str:
    """Add a new task to the task list"""
    tasks = load_tasks()
    
    # Generate unique ID
    task_id = f"task_{len(tasks) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Parse due date if provided
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except ValueError:
            pass
    
    new_task = Task(
        id=task_id,
        title=title,
        description=description,
        priority=priority,
        due_date=parsed_due_date,
        created_at=datetime.now()
    )
    
    tasks.append(new_task)
    save_tasks(tasks)
    
    return f"Task '{title}' added successfully with ID: {task_id}"

@tool
def list_tasks(status: str = "all") -> str:
    """List all tasks or tasks with specific status"""
    tasks = load_tasks()
    
    if not tasks:
        return "No tasks found. You can add a new task by saying 'add task' followed by the task details."
    
    if status != "all":
        tasks = [task for task in tasks if task.status == status]
    
    if not tasks:
        return f"No tasks found with status '{status}'"
    
    result = f"Here are your tasks ({status}):\n\n"
    for i, task in enumerate(tasks, 1):
        due_info = f" (Due: {task.due_date.strftime('%Y-%m-%d %H:%M')})" if task.due_date else ""
        result += f"{i}. [{task.priority.upper()}] {task.title}{due_info}\n"
        if task.description:
            result += f"   Description: {task.description}\n"
        result += f"   Status: {task.status}\n\n"
    
    return result

@tool
def complete_task(task_title: str) -> str:
    """Mark a task as completed"""
    tasks = load_tasks()
    
    for task in tasks:
        if task.title.lower() == task_title.lower():
            task.status = "completed"
            task.completed_at = datetime.now()
            save_tasks(tasks)
            return f"Task '{task.title}' marked as completed!"
    
    return f"Task '{task_title}' not found. Please check the task title and try again."

@tool
def delete_task(task_title: str) -> str:
    """Delete a task from the task list"""
    tasks = load_tasks()
    
    for i, task in enumerate(tasks):
        if task.title.lower() == task_title.lower():
            removed_task = tasks.pop(i)
            save_tasks(tasks)
            return f"Task '{removed_task.title}' deleted successfully!"
    
    return f"Task '{task_title}' not found. Please check the task title and try again."

@tool
def update_task_priority(task_title: str, priority: str) -> str:
    """Update the priority of a task"""
    if priority not in ["low", "medium", "high"]:
        return "Priority must be 'low', 'medium', or 'high'"
    
    tasks = load_tasks()
    
    for task in tasks:
        if task.title.lower() == task_title.lower():
            task.priority = priority
            save_tasks(tasks)
            return f"Task '{task.title}' priority updated to {priority}!"
    
    return f"Task '{task_title}' not found. Please check the task title and try again."

@tool
def get_task_summary() -> str:
    """Get a summary of all tasks"""
    tasks = load_tasks()
    
    if not tasks:
        return "You have no tasks. Great job staying on top of things!"
    
    pending = len([t for t in tasks if t.status == "pending"])
    in_progress = len([t for t in tasks if t.status == "in_progress"])
    completed = len([t for t in tasks if t.status == "completed"])
    
    overdue = len([t for t in tasks if t.due_date and t.due_date < datetime.now() and t.status != "completed"])
    
    summary = f"Task Summary:\n"
    summary += f"- Total tasks: {len(tasks)}\n"
    summary += f"- Pending: {pending}\n"
    summary += f"- In Progress: {in_progress}\n"
    summary += f"- Completed: {completed}\n"
    
    if overdue > 0:
        summary += f"- Overdue: {overdue}\n"
    
    return summary