# --- THE SCHOOL BOT BRAIN ---
from dotenv import load_dotenv
load_dotenv()

from google.adk import agents
from google.adk import runners
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.sessions import InMemorySessionService

session_memory = InMemorySessionService()

school_agent = agents.LlmAgent(
    name="SchoolBot",
    model="gemini-2.0-flash",
    instruction="""You are 'SchoolBot', a helpful assistant for parents and students in India.
    
    # GREETING & MENU
    - When the user says "Hi", "Hello", or "Start", respond with this menu:
        "Welcome to SchoolBot! 🏫 I can help you find the best schools in your city. 
        Please choose an option or type your query:
        1. Find CBSE Schools
        2. Find ICSE Schools
        3. Find IGCSE/International Schools
        4. Find Government/KVs
        5. Admission FAQs & Fees"

    # HANDLING OPTIONS
    - **Option 1-4:** Ask for the **City** and **Locality** if not provided. 
        - Use Google Search to find top-rated schools in that specific category and city.
        - Try to provide a list of 3-5 schools with their location and a brief highlight (e.g., 'Known for sports' or 'Top results').
    - **Option 5 (FAQs & Fees):** Search for "admission dates [Year] [City] schools" or "average fee structure of [Board] schools in [City]".

    # GENERAL BEHAVIOR
    - Always use the Google Search tool for up-to-date info.
    - If a user asks for a specific locality (e.g., 'Adyar' in Chennai), prioritize schools in that area.
    - Be professional, encouraging, and clear.
    """,
    tools=[GoogleSearchTool()] 
)

# Update the Runner and App Name
APP_NAME = "SchoolBotApp"
runner = runners.Runner(agent=school_agent, session_service=session_memory, app_name=APP_NAME)

if __name__ == "__main__":
    import sys
    from google.genai import types

    # Create a session for local testing
    session_id = "cli_demo_session"
    user_id = "cli_user"
    try:
        session_memory.create_session_sync(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    except:
        pass # Session might already exist if we reload

    print(f"--- SchoolBot CLI (Session: {session_id}) ---")
    print("Type 'quit' to exit.")

    while True:
        try:
            text = input("\nYou: ")
            if text.lower() in ['quit', 'exit']:
                break
            
            msg = types.Content(parts=[types.Part(text=text)])
            print("Bot: ", end="", flush=True)
            for event in runner.run(user_id=user_id, session_id=session_id, new_message=msg):
                if hasattr(event, 'text'):
                     print(event.text, end="", flush=True)
                elif hasattr(event, 'part') and hasattr(event.part, 'text'):
                     print(event.part.text, end="", flush=True)
            print()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")