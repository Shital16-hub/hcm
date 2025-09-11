# agent_final.py - FINAL working LangGraph agent with proper streaming
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    google,
    noise_cancellation,
    silero,
    openai,
    langchain
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from task_manager.graph_fixed import create_task_manager_graph

load_dotenv(".env.local")

class TaskManagerAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a helpful voice-activated daily task manager. "
                        "Help users manage their tasks through natural voice commands."
        )

async def entrypoint(ctx: agents.JobContext):
    print("🚀 Starting LangGraph task manager agent...")
    
    # Create the LangGraph task manager workflow with proper streaming
    print("📊 Creating LangGraph workflow...")
    task_graph = create_task_manager_graph()
    print("✅ LangGraph workflow created successfully")
    
    # Use LangGraph with LiveKit adapter
    llm_to_use = langchain.LLMAdapter(graph=task_graph)
    print("🔗 LangGraph adapter created with streaming support")
    
    print("🎙️ Creating agent session...")
    
    # Create agent session with working configuration
    session = AgentSession(
        # Google Cloud STT
        stt=google.STT(
            model="long",
            spoken_punctuation=False,
            languages=["en-US"]
        ),
        
        # LangGraph-powered LLM with proper streaming
        llm=llm_to_use,
        
        # OpenAI TTS (proven to work)
        tts=openai.TTS(
            voice="alloy",
            model="tts-1",
        ),
        
        # Voice Activity Detection
        vad=silero.VAD.load(),
        
        # Turn detection
        turn_detection=MultilingualModel(),
    )

    print("🏁 Starting session...")
    await session.start(
        room=ctx.room,
        agent=TaskManagerAgent(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    print("👋 Generating initial greeting...")
    await session.generate_reply(
        instructions="Greet the user warmly and introduce yourself as their voice-activated "
                    "task manager. Let them know they can add tasks, list tasks, "
                    "mark tasks as complete, or get a task summary. Ask what they'd like to do."
    )
    print("✅ Initial greeting generated successfully")

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))