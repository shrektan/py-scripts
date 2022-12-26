"""一个无敌简单的web服务器
"""
import socket

WEBROOT = "./webroot"

def handle_client(c: socket.socket, addr: str):
    print(f"{addr} connected")
    with c:
        request = c.recv(1024)
        headers = request.split(b"\r\n")
        file = headers[0].split()[1].decode()
        if file == "/":
            file = "/index.html"
        try:
            with open(WEBROOT + file, "rb") as f:
                content = f.read()
            response = b"HTTP/1.0 200 OK\r\n\r\n" + content
        except FileNotFoundError:
            response = b"HTTP/1.0 404 NOT FOUND\r\n\r\nFile not found!"
        c.sendall(response)

# os.chdir(os.path.dirname(os.path.abspath(__file__)))
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("0.0.0.0", 80))
    s.listen()
    while True:
        c, addr = s.accept()
        handle_client(c, addr)
