# agent_simple.py - Working version without LangGraph
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    google,
    elevenlabs, 
    noise_cancellation,
    silero,
    openai  # Use simple OpenAI instead of LangGraph
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(".env.local")

class TaskManagerAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful voice-activated daily task manager assistant. 
            
            Your role is to help users manage their daily tasks through voice commands. You can:
            - Add new tasks with descriptions, priorities, and due dates
            - List all tasks or filter by status (pending, in_progress, completed)
            - Mark tasks as completed
            - Delete tasks
            - Update task priorities
            - Provide task summaries
            
            When interacting with users:
            - Be conversational and friendly
            - Ask for clarification when task details are unclear
            - Provide confirmations after actions
            - Keep responses concise but informative
            
            Always respond to greetings warmly and explain what you can help with.
            For now, just acknowledge task requests and explain that task management features are being set up."""
        )

async def entrypoint(ctx: agents.JobContext):
    print("🚀 Starting entrypoint...")
    
    print("🎙️ Creating agent session with simple OpenAI...")
    
    # Create agent session with simple OpenAI LLM
    session = AgentSession(
        # Google Cloud STT
        stt=google.STT(
            model="long",
            spoken_punctuation=False,
            languages=["en-US"]
        ),
        
        # Simple OpenAI LLM (this should work)
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.1,
        ),
        
        # OpenAI TTS (more reliable than ElevenLabs)
        tts=openai.TTS(
            voice="alloy",
            model="tts-1",
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