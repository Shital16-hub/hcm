# agent.py - Fixed with Debug Logging
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    google,
    elevenlabs, 
    noise_cancellation,
    silero,
    langchain
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from task_manager.graph import create_task_manager_graph

load_dotenv(".env.local")

class TaskManagerAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a helpful voice-activated daily task manager. "
                        "Help users manage their tasks through natural voice commands."
        )

async def entrypoint(ctx: agents.JobContext):
    print("🚀 Starting entrypoint...")
    
    try:
        # Create the LangGraph task manager workflow
        print("📊 Creating LangGraph workflow...")
        task_graph = create_task_manager_graph()
        print("✅ LangGraph workflow created successfully")
    except Exception as e:
        print(f"❌ Error creating LangGraph workflow: {e}")
        # Fallback to simple OpenAI LLM
        from livekit.plugins import openai
        print("🔄 Falling back to simple OpenAI LLM...")
        llm_to_use = openai.LLM(model="gpt-4o-mini", temperature=0.1)
    else:
        llm_to_use = langchain.LLMAdapter(graph=task_graph)
    
    print("🎙️ Creating agent session...")
    
    # Create agent session
    session = AgentSession(
        # Google Cloud STT
        stt=google.STT(
            model="long",
            spoken_punctuation=False,
            languages=["en-US"]
        ),
        
        # LLM (either LangGraph or fallback)
        llm=llm_to_use,
        
        # ElevenLabs TTS
        tts=elevenlabs.TTS(
            voice_id="ODq5zmih8GrVes37Dizd",
            model="eleven_multilingual_v2",
            language="en"
        ),
        
        # Voice Activity Detection
        vad=silero.VAD.load(),
        
        # Turn detection for natural conversation flow
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
    # Generate initial greeting
    try:
        await session.generate_reply(
            instructions="Greet the user warmly and introduce yourself as their voice-activated "
                        "task manager. Say: 'Hello! I'm your voice-activated task manager. "
                        "I can help you add tasks, list your tasks, mark them as complete, "
                        "or give you a summary. What would you like to do?'"
        )
        print("✅ Initial greeting generated successfully")
    except Exception as e:
        print(f"❌ Error generating greeting: {e}")

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))