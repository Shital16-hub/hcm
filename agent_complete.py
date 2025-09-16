from dotenv import load_dotenv
import logging
import os
from livekit import agents
from livekit.agents import AgentSession, Agent, JobContext, WorkerOptions, RoomInputOptions
from livekit.plugins import noise_cancellation, silero, google, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from task_manager.graph_simple import create_task_manager_graph
from adapter.langgraph import LangGraphAdapter
from livekit.plugins import elevenlabs


load_dotenv(".env.local")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskManagerAgent(Agent):
    def __init__(self):
        super().__init__(instructions="You are a helpful voice task manager.")

async def entrypoint(ctx: JobContext):
    logger.info("🚀 Starting SMOOTH Voice Task Manager...")
    
    # Verify credentials
    google_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_key:
        raise ValueError("Missing OPENAI_API_KEY")
    if not os.path.exists(google_creds):
        raise ValueError("Missing Google Cloud credentials")
        
    logger.info("✅ All credentials verified")
    
    # Create optimized ReAct agent
    task_graph = create_task_manager_graph()
    logger.info("✅ Optimized ReAct agent created")
    
    # Create session with FIXED configuration
    session = AgentSession(
        llm=LangGraphAdapter(
            graph=task_graph,
            config={}
        ),
        
        # Google Cloud STT
        stt=google.STT(
            model="latest_long",
            languages=["en-US"],
            detect_language=False,
            interim_results=True
        ),
        
        # OpenAI TTS
        tts=elevenlabs.TTS(
        voice_id="pNInz6obpgDQGcFmaJgB",
        model="eleven_multilingual_v2"
        ),
        
        # FIXED: Use default VAD configuration (no custom parameters)
        turn_detection=MultilingualModel(),
        vad=silero.VAD.load(),  # <-- FIXED: Remove all unsupported parameters
        
        # Performance optimizations
        preemptive_generation=True,
        min_endpointing_delay=0.2,
        max_endpointing_delay=2.0,
    )
    
    await session.start(
        agent=TaskManagerAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
            close_on_disconnect=False
        ),
    )
    
    logger.info("🎤 SMOOTH: Voice Task Manager Ready!")
    logger.info("✅ Optimized for smooth voice interaction")
    
    # Brief, clear greeting
    await session.say(
        "Hi! I'm your voice task manager. Say 'add task buy groceries' or 'list my tasks' to get started."
    )
    
    await ctx.connect()

if __name__ == "__main__":
    agents.cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
