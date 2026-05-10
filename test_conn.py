import os
from dotenv import load_dotenv
load_dotenv()
url = os.environ.get("DATABASE_URL")
print(f"URL: {url}")
import socket
host = "ep-withered-fire-amdrqurg.c-5.us-east-1.aws.neon.tech"
try:
    print(f"IP: {socket.gethostbyname(host)}")
except Exception as e:
    print(f"DNS Error: {e}")
