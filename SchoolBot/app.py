
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from bot import runner, session_memory, APP_NAME
from google.genai import types
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/bot", methods=["POST"])
@app.route("/webhook", methods=["POST"])
def bot():
    """Endpoint for Twilio webhooks"""
    incoming_msg = request.values.get("Body", "").strip()
    sender_id = request.values.get("From", "").replace("whatsapp:", "")
    
    # Use sender_number as user_id and session_id for simplicity in this demo
    user_id = sender_id
    session_id = f"session_{sender_id}"

    logger.info(f"Received message from {user_id}: {incoming_msg}")

    # Ensure session exists
    try:
        session_memory.create_session_sync(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )
    except Exception:
        # Session likely already exists
        pass

    # sending response
    resp = MessagingResponse()
    msg = resp.message()
    
    if not incoming_msg:
        msg.body("I didn't receive any text.")
        return str(resp)

    try:
        # Run the agent
        # Create Content object
        content_msg = types.Content(parts=[types.Part(text=incoming_msg)])
        
        # Collect full response text from the agent
        full_response_text = ""
        for event in runner.run(user_id=user_id, session_id=session_id, new_message=content_msg):
            # Extract text from various event types/structures
            text_chunk = ""
            if hasattr(event, 'text'):
                text_chunk = event.text
            elif hasattr(event, 'part') and hasattr(event.part, 'text'):
                text_chunk = event.part.text
            elif hasattr(event, 'parts'):
                 for p in event.parts:
                     if hasattr(p, 'text'): text_chunk += p.text
            elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                 for p in event.content.parts:
                     if hasattr(p, 'text'): text_chunk += p.text
            
            if text_chunk:
                full_response_text += text_chunk
        
        if full_response_text:
            msg.body(full_response_text)
        else:
            msg.body("Sorry, I couldn't generate a response.")
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        msg.body("An internal error occurred. Please try again later.")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
