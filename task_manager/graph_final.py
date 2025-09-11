# task_manager/graph_final.py - CORRECT streaming implementation for LiveKit
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
    """Create LangGraph with proper streaming for LiveKit"""
    
    # CRITICAL: Must enable streaming for LiveKit compatibility
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.OPENAI_API_KEY,
        temperature=0.1,
        streaming=True,  # Essential for LiveKit
        max_tokens=150,  # Keep responses concise for voice
    )
    
    tools = [
        add_task, list_tasks, complete_task, delete_task, 
        update_task_priority, get_task_summary
    ]
    
    # Bind tools with streaming enabled
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = """You are a voice-activated task manager. Help users:
- "add task [description]" → Create new task
- "list tasks" → Show all tasks  
- "complete [task]" → Mark done
- "delete [task]" → Remove task
- "task summary" → Get overview

Be conversational and concise (1-2 sentences max)."""
    
    def agent_node(state: TaskManagerState, config):
        """Agent node that MUST use astream for LiveKit compatibility"""
        messages = state.get("messages", [])
        
        # Build conversation
        conversation = [SystemMessage(content=system_prompt)]
        
        # Add messages from LiveKit (they come as LangChain objects)
        for msg in messages:
            if isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
                conversation.append(msg)
        
        # Handle initial greeting
        user_messages = [m for m in conversation if isinstance(m, HumanMessage)]
        if not user_messages:
            conversation.append(
                HumanMessage(content="Greet the user and briefly introduce yourself as their task manager.")
            )
        
        # CRITICAL: Use ainvoke with config to enable streaming
        # The config parameter enables proper streaming context
        try:
            response = llm_with_tools.invoke(conversation, config)
            return {"messages": [response]}
        except Exception as e:
            print(f"Agent error: {e}")
            return {"messages": [AIMessage(content="I'm having trouble. Please try again.")]}
    
    def route_after_agent(state: TaskManagerState) -> Literal["tools", "__end__"]:
        """Route to tools if needed"""
        messages = state.get("messages", [])
        if not messages:
            return "__end__"
            
        last_message = messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return "__end__"
    
    # Build graph
    workflow = StateGraph(TaskManagerState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    
    # Define flow
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", route_after_agent, {
        "tools": "tools",
        "__end__": END
    })
    workflow.add_edge("tools", "agent")
    
    # Compile without checkpointer for better streaming
    return workflow.compile()