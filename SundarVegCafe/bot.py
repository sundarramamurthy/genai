import os
import asyncio
from flask import Flask, request
from twilio.rest import Client
from google.genai import types
from google.adk import agents
from google.adk import runners
from google.adk import sessions as services
from google.adk import tools
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

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
# This memory service ensures the bot remembers Adipa and Aaakuttyma
session_memory = services.InMemorySessionService()


# SKILL 1: Reading the menu.csv inside the data folder
def fetch_menu(query: str):
    """Look up menu items and prices."""
    file_path = os.path.join("data", "menu.csv")
    try:
        df = pd.read_csv(file_path)
        # This formats the CSV into a nice list for WhatsApp
        menu_list = "Our Menu:\n"
        for _, row in df.iterrows():
            menu_list += f"- {row['item']} - ₹{row['price']} ({row['description']})\n"
        return menu_list
    except:
        return "I'm sorry, I can't see the menu right now."

# SKILL 2: Writing the order to a text file
def save_order(order_summary: str):
    """Save a food order to the system."""
    file_path = os.path.join("data", "orders.txt")
    with open(file_path, "a") as f:
        f.write(f"{datetime.now()}: {order_summary}\n")
    return "Thank you! Your order has been placed."

# Wrapping them so the Google ADK can use them
# Wrapping them so the Google ADK can use them
menu_tool = tools.FunctionTool(fetch_menu)
order_tool = tools.FunctionTool(save_order)


# --- THE CAFE BRAIN ---
# We tell the AI who it is and how to behave
cafe_agent = agents.LlmAgent(
    name="SundarVegCafeBot",
    model="gemini-2.0-flash",
    instruction="""You are the assistant for SundarVegCafe. 
    - Start conversations with "Welcome to Sundar's Kitchen".
    - Use 'lookup_menu' to see food items and prices.
    - Always display menu items as a bulleted list with food emojis.
    - If someone orders a Masala Dosa, suggest our Filter Coffee.
    - if someone orders a Paneer Butter Masala, suggest our Roti.
    - if someone orders a pongal, suggest our Vada.
    - Use 'place_order' to save the final order once they confirm.
    - Be warm and use emojis!""" ,
    tools=[menu_tool, order_tool] # We will create these tools in the next step
)

# The Runner connects the Brain to the Memory
APP_NAME = "SundarVegCafeApp"
runner = runners.Runner(agent=cafe_agent, session_service=session_memory, app_name=APP_NAME)

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