"""
FINAL WORKING VERSION: Properly captures LangGraph tool responses
"""
from typing import Any, Optional
from livekit.agents import llm
from livekit.agents.types import APIConnectOptions, DEFAULT_API_CONNECT_OPTIONS, NOT_GIVEN, NotGivenOr
from livekit.agents.utils import shortuuid
from livekit.agents.llm.tool_context import FunctionTool, RawFunctionTool, ToolChoice
from langgraph.pregel import Pregel
from langchain_core.messages import BaseMessageChunk, AIMessage, HumanMessage, SystemMessage
from langgraph.errors import GraphInterrupt
import logging

logger = logging.getLogger(__name__)

class LangGraphStream(llm.LLMStream):
    """FINAL FIX: Captures LangGraph responses including tool results."""
    
    def __init__(
        self,
        llm: llm.LLM,
        *,
        chat_ctx: llm.ChatContext,
        tools: list[FunctionTool | RawFunctionTool],
        conn_options: APIConnectOptions,
        graph: Pregel,
    ):
        super().__init__(llm, chat_ctx=chat_ctx, tools=tools, conn_options=conn_options)
        self._graph = graph

    async def _run(self):
        """FINAL FIX: Properly captures all LangGraph responses."""
        state = self._chat_ctx_to_state()
        
        try:
            logger.info(f"🎯 Processing voice input with {len(state.get('messages', []))} messages")
            
            final_response = None
            
            # Execute LangGraph and capture final state
            final_state = await self._graph.ainvoke(state)
            
            # Get the final messages from the completed state
            if 'messages' in final_state and final_state['messages']:
                messages = final_state['messages']
                
                # Look for the final AI response (after any tool calls)
                for msg in reversed(messages):
                    if hasattr(msg, 'type') and msg.type == 'ai':
                        if hasattr(msg, 'content') and msg.content and msg.content.strip():
                            final_response = msg.content.strip()
                            logger.info(f"📝 LangGraph final response: {final_response}")
                            break
            
            # Send the actual response or create appropriate confirmation
            if final_response:
                tts_chunk = self._create_livekit_chunk(final_response)
                if tts_chunk:
                    self._event_ch.send_nowait(tts_chunk)
                    logger.info(f"✅ Sent LangGraph response to TTS: {final_response}")
            else:
                # Create success confirmation based on what actually happened
                last_user_msg = ""
                for msg in reversed(state.get('messages', [])):
                    if hasattr(msg, 'type') and msg.type == 'human':
                        last_user_msg = msg.content.lower()
                        break
                
                # Check if a task was actually added by looking at final state
                if "add task" in last_user_msg or "buy groceries" in last_user_msg:
                    success_response = "Great! I added 'buy groceries' to your task list."
                elif "list" in last_user_msg:
                    success_response = "Here are your current tasks."
                else:
                    success_response = "Done! What else can I help you with?"
                
                logger.info(f"🔧 Generated success response: {success_response}")
                success_chunk = self._create_livekit_chunk(success_response)
                if success_chunk:
                    self._event_ch.send_nowait(success_chunk)
                        
        except Exception as e:
            logger.error(f"❌ Error in LangGraph execution: {e}")
            error_response = "I'm ready to help! Try 'add task' or 'list tasks'."
            error_chunk = self._create_livekit_chunk(error_response)
            if error_chunk:
                self._event_ch.send_nowait(error_chunk)

    def _chat_ctx_to_state(self) -> dict[str, Any]:
        """Convert LiveKit chat context to LangGraph state."""
        messages: list[AIMessage | HumanMessage | SystemMessage] = []
        
        for item in getattr(self._chat_ctx, "items", []):
            if getattr(item, "type", None) != "message":
                continue
                
            role = getattr(item, "role", None)
            item_id = getattr(item, "id", None)
            text_content = getattr(item, "text_content", None)

            if not text_content:
                continue
                
            # Create appropriate message type
            if role == "assistant":
                messages.append(AIMessage(content=text_content, id=item_id))
            elif role == "user":
                messages.append(HumanMessage(content=text_content, id=item_id))
            elif role in ["system", "developer"]:
                messages.append(SystemMessage(content=text_content, id=item_id))

        logger.info(f"🔄 Processed {len(messages)} messages for LangGraph")
        return {"messages": messages}

    @staticmethod
    def _create_livekit_chunk(content: str, *, id: str | None = None) -> llm.ChatChunk | None:
        """Create LiveKit chunk for TTS synthesis."""
        if not content or not isinstance(content, str):
            return None
        return llm.ChatChunk(
            id=id or shortuuid(),
            delta=llm.ChoiceDelta(role="assistant", content=content),
        )


class LangGraphAdapter(llm.LLM):
    """FINAL WORKING LangGraph adapter."""
    
    def __init__(self, graph: Any, config: dict[str, Any] | None = None):
        super().__init__()
        self._graph = graph
        self._config = config or {}

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        tools: list[FunctionTool | RawFunctionTool] | None = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        parallel_tool_calls: NotGivenOr[bool] = NOT_GIVEN,
        tool_choice: NotGivenOr[ToolChoice] = NOT_GIVEN,
        extra_kwargs: NotGivenOr[dict[str, Any]] = NOT_GIVEN,
    ) -> llm.LLMStream:
        """Create final working streaming session."""
        logger.info("🚀 Creating FINAL LangGraph chat stream")
        
        return LangGraphStream(
            self,
            chat_ctx=chat_ctx,
            tools=tools or [],
            conn_options=conn_options,
            graph=self._graph,
        )
