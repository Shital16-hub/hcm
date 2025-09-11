# task_manager/graph_fixed.py - CORRECT streaming implementation for LiveKit
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict
from typing import Annotated

from .tools import (
    add_task, list_tasks, complete_task, delete_task, 
    update_task_priority, get_task_summary
)
from config.settings import settings

class TaskManagerState(TypedDict):
    messages: Annotated[list, add_messages]

def create_task_manager_graph():
    """Create LangGraph workflow with proper streaming for LiveKit"""
    
    # Initialize OpenAI LLM with streaming enabled
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.OPENAI_API_KEY,
        temperature=0.1,
        streaming=True,  # Critical for LiveKit compatibility
        max_tokens=200,  # Keep responses concise for voice
    )
    
    # Available tools
    tools = [
        add_task, list_tasks, complete_task, delete_task, 
        update_task_priority, get_task_summary
    ]
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # System prompt optimized for voice
    system_prompt = """You are a voice-activated task manager. Help users:

COMMANDS:
- "add task [description]" → Create new task
- "list tasks" → Show all tasks  
- "complete [task title]" → Mark task done
- "delete [task title]" → Remove task
- "task summary" → Get overview

Keep responses short and conversational. Always confirm actions clearly."""
    
    async def agent_node(state: TaskManagerState):
        """Agent node using astream() for proper LiveKit streaming"""
        messages = state.get("messages", [])
        
        # Build conversation with system prompt
        conversation = [SystemMessage(content=system_prompt)]
        
        # Add existing messages from LiveKit
        for msg in messages:
            if isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
                conversation.append(msg)
        
        # Check if this is initial greeting
        user_messages = [m for m in conversation if isinstance(m, HumanMessage)]
        if not user_messages:
            conversation.append(
                HumanMessage(content="Please greet the user and briefly introduce your task management capabilities.")
            )
        
        try:
            # CRITICAL: Use astream() instead of invoke() for LiveKit streaming
            response_chunks = []
            async for chunk in llm_with_tools.astream(conversation):
                response_chunks.append(chunk)
            
            # Combine chunks into final response
            if response_chunks:
                final_response = response_chunks[-1]  # Get the final chunk
                return {"messages": [final_response]}
            else:
                return {"messages": [AIMessage(content="I'm ready to help with your tasks.")]}
                
        except Exception as e:
            print(f"Agent node error: {e}")
            return {"messages": [AIMessage(content="I'm having trouble. Please try again.")]}
    
    def route_after_agent(state: TaskManagerState) -> Literal["tools", "__end__"]:
        """Route to tools if needed, otherwise end"""
        messages = state.get("messages", [])
        if not messages:
            return "__end__"
            
        last_message = messages[-1]
        
        # Check if LLM wants to use tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        return "__end__"
    
    # Build the graph
    workflow = StateGraph(TaskManagerState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    
    # Define flow
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "tools": "tools",
            "__end__": END
        }
    )
    workflow.add_edge("tools", "agent")
    
    # Compile for LiveKit compatibility
    return workflow.compile()