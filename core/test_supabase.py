from dotenv import load_dotenv
import os
import socket

load_dotenv()

url = os.getenv("SUPABASE_URL")

print("SUPABASE_URL =", url)

try:
    host = url.replace("https://", "").replace("http://", "")
    ip = socket.gethostbyname(host)

    print("✅ Host resolved")
    print("IP:", ip)

except Exception as e:
    print("❌ DNS FAILED")
    print(e)