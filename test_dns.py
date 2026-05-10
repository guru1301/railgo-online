import socket
hosts = [
    "ep-withered-fire-amdrqurg.c-5.us-east-1.aws.neon.tech",
    "ep-withered-fire-amdrqurg.us-east-1.aws.neon.tech"
]
for host in hosts:
    try:
        ip = socket.gethostbyname(host)
        print(f"{host} -> {ip}")
    except Exception as e:
        print(f"{host} -> Error: {e}")
