# RailBot 🚆

**RailBot** is an intelligent WhatsApp chatbot powered by Google Gen AI (Gemini 2.0 Flash) that helps users with Indian Railways inquiries. It uses Google Search to provide real-time information about trains, seat availability, and station amenities.

## Features

*   **Train Information:** Get routes, stops, and travel times.
*   **Seat Availability:** Check live seat status (e.g., Available, WL) for specific dates and classes. Uses smart search queries to target reliable sources like RailYatri and Ixigo.
*   **Station Facilities:** Find amenities like AC waiting rooms at railway stations.
*   **City Info & Tourism:** Get quick city guides and "places to visit" recommendations.
*   **Interactive Menu:** Easy-to-use numbered menu system on WhatsApp.

## Tech Stack

*   **AI:** Google Gemini 2.0 Flash (via Google Gen AI SDK / ADK)
*   **Backend:** Python, Flask
*   **Messaging:** Twilio API (WhatsApp)
*   **Search:** Google Search Tool (ADK)
*   **Tunneling:** Ngrok (for local development)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sundarramamurthy/genai.git
    cd genai
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_google_api_key
    TWILIO_ACCOUNT_SID=your_twilio_sid
    TWILIO_AUTH_TOKEN=your_twilio_auth_token
    NGROK_AUTHTOKEN=your_ngrok_token
    ```

## Usage

1.  **Start the Ngrok Tunnel:**
    This script launches ngrok on port 5000 and prints the public URL.
    ```bash
    python start_tunnel.py
    ```
    *Copy the generated HTTPS URL (e.g., `https://xyz.ngrok-free.app`).*

2.  **Configure Twilio:**
    - Go to your Twilio Console > Messaging > Sandbox Settings.
    - Paste the Ngrok URL into the "When a message comes in" field (append `/webhook`), e.g., `https://xyz.ngrok-free.app/webhook`.

3.  **Start the Bot:**
    In a new terminal window (with venv activated):
    ```bash
    python bot.py
    ```

4.  **Chat on WhatsApp:**
    Send **"Hi"** to your Twilio Sandbox number to see the main menu!
