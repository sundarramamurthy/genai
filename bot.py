import os
import asyncio
from flask import Flask, request
from twilio.rest import Client
from google.genai import types
from google.adk import agents
from google.adk import runners
from google.adk import sessions as services
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk import tools
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- 1. SETTING UP THE CONNECTIONS ---
# Keys from .env
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Twilio provides a sandbox number (usually +1 415 523 8886)
TWILIO_FROM_NUMBER = "whatsapp:+14155238886" 

twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)

# --- 2. THE ADK AGENT (THE BRAIN) ---
session_memory = services.InMemorySessionService()

# --- THE RAIL BOT BRAIN ---
# We tell the AI who it is and how to behave
rail_agent = agents.LlmAgent(
    name="RailBot",
    model="gemini-2.0-flash",
    instruction="""You are a helpful RailBot assistant.
    
    # GREETING & MENU
    - When the user says "Hi", "Hello", "Start", or initiates conversation, **ALWAYS** respond with this exact menu:
        "Welcome to RailBot! 🚆 How can I assist you today? Please choose an option:
        1. Train information (Routes, Stops, Travel Time)
        2. Check seat availability
        3. Station facility (AC Waiting Rooms, etc.)
        4. City info
        5. Places to visit"

    # HANDLING OPTIONS
    - **Option 1 (Train Info):** Ask for the source and destination stations if not provided. Use Google Search to find train lists, stops, and schedules.
    - **Option 2 (Seat Availability):** 
        - Ask for **From Station**, **To Station**, and **Date of Travel** if missing.
        - **Search Strategy:** Primary: "RailYatri seat availability [Train] [Date]", Secondary: "Ixigo".
        - **Reporting:** Try to show availability by CLASS (2S, CC, SL). Fallback to general text if needed.
    - **Option 3 (Station Facility):** Ask for the station name. Search for "passenger amenities at [Station Name] railway station" or "AC waiting room at [Station]".
    - **Option 4 (City Info):** Ask for the city name. Provide a brief overview (weather, best time to visit, key facts).
    - **Option 5 (Places to Visit):** Ask for the city/location. List top tourist attractions with brief descriptions.

    # GENERAL BEHAVIOR
    - Be concise and helpful.
    - Always use the Google Search tool to fetch real-time information.
    """,
    tools=[GoogleSearchTool()] 
)

# The Runner connects the Brain to the Memory
APP_NAME = "RailBotApp"
runner = runners.Runner(agent=rail_agent, session_service=session_memory, app_name=APP_NAME)

# --- 3. THE "BRIDGE" SERVER ---
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def incoming_whatsapp():
    # A. Get the message and the phone number of who sent it
    incoming_msg = request.values.get('Body', '').lower()
    sender_number = request.values.get('From', '')

    # B. Ask the ADK Agent for an answer
    # We use asyncio.run because ADK is "asynchronous" (fast/non-blocking)
    reply_text = asyncio.run(ask_the_brain(sender_number, incoming_msg))

    # C. Send the answer back to WhatsApp
    twilio_client.messages.create(
        body=reply_text,
        from_=TWILIO_FROM_NUMBER,
        to=sender_number
    )
    return "OK", 200

async def ask_the_brain(phone, text):
    # Ensure session exists
    session = await session_memory.get_session(app_name=APP_NAME, user_id=phone, session_id=phone)
    if not session:
        await session_memory.create_session(app_name=APP_NAME, user_id=phone, session_id=phone)

    # Convert text to ADK format
    content = types.Content(role="user", parts=[types.Part(text=text)])
    
    # Run the agent and get the final result
    async for event in runner.run_async(session_id=phone, user_id=phone, new_message=content):
        if event.is_final_response():
            return "".join(p.text for p in event.content.parts)
    return "I am a bit confused right now."

if __name__ == "__main__":
    app.run(port=5000)