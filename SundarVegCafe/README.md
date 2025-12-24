# SundarVegCafe Bot 🥗

**SundarVegCafe Bot** is a friendly WhatsApp assistant for "Sundar's Kitchen", designed to help customers browse the menu, get food recommendations, and place orders seamlessly.

Powered by **Google Gemini 2.0 Flash** and the **Google Gen AI SDK**.

## Features

*   **📜 View Menu**: Browse a delicious list of vegetarian dishes with prices.
*   **🤖 Smart Recommendations**: 
    *   Orders *Masala Dosa*? We suggest *Filter Coffee*.
    *   Orders *Pongal*? We suggest *Vada*.
*   **📝 Order Placement**: Confirm your order and have it saved to the kitchen system.
*   **💬 Natural Conversation**: Chat naturally to ask about food items.

## Tech Stack

*   **AI Model**: Google Gemini 2.0 Flash
*   **Framework**: Google Gen AI ADK (Agent Development Kit)
*   **Backend**: Python & Flask
*   **Messaging**: Twilio API for WhatsApp

## Setup & Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/sundarramamurthy/genai.git
    cd genai/SundarVegCafe
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables**:
    Create a `.env` file with your keys:
    ```env
    GOOGLE_API_KEY=your_google_key
    TWILIO_ACCOUNT_SID=your_twilio_sid
    TWILIO_AUTH_TOKEN=your_twilio_token
    ```

4.  **Run the Bot**:
    ```bash
    python bot.py
    ```

5.  **Connect WhatsApp**:
    *   Use **Ngrok** to expose port 5000: `ngrok http 5000`
    *   Update your Twilio Sandbox Webhook with the Ngrok URL (e.g., `https://your-url.ngrok.io/webhook`).
