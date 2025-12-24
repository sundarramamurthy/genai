from pyngrok import ngrok
import time

# Open a HTTP tunnel on the default port 5000
# <NgrokTunnel: "http://<public_sub>.ngrok.io" -> "http://localhost:5000">
public_url = ngrok.connect(5000).public_url

print(f"\n\nNGROK PUBLIC URL: {public_url}")
print("Copy the URL above and paste it into your Twilio Sandbox Configuration.")
print("Keep this script running or the tunnel will close.\n")

# Keep the script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Closing tunnel...")
    ngrok.kill()
