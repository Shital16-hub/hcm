# simple_agent.py - For testing without LangGraph
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    google,
    elevenlabs, 
    noise_cancellation,
    silero,
    openai  # Use direct OpenAI instead of LangGraph
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(".env.local")

class SimpleTaskManagerAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a helpful voice-activated daily task manager. "
                        "Help users manage their tasks through natural voice commands. "
                        "Always respond warmly to greetings and explain what you can help with."
        )

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        # Google Cloud STT
        stt=google.STT(
            model="long",
            spoken_punctuation=False,
            languages=["en-US"]
        ),
        
        # Direct Azure OpenAI LLM (simpler than LangGraph for testing)
        llm=openai.LLM.with_azure(
            azure_deployment="gpt-4o",  # Replace with your deployment name
            azure_endpoint="https://your-endpoint.openai.azure.com/",  # Replace with your endpoint
            api_key="your-api-key",  # Replace with your API key
            api_version="2024-10-01-preview",
        ),
        
        # ElevenLabs TTS
        tts=elevenlabs.TTS(
            voice_id="ODq5zmih8GrVes37Dizd",
            model="eleven_multilingual_v2",
            language="en"
        ),
        
        # Voice Activity Detection
        vad=silero.VAD.load(),
        
        # Turn detection
        turn_detection=MultilingualModel(),
    )

    await session.start(
        room=ctx.room,
        agent=SimpleTaskManagerAgent(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Generate initial greeting
    await session.generate_reply(
        instructions="Greet the user warmly and introduce yourself as their voice-activated "
                    "task manager. Explain that you can help them manage tasks."
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))