import socket
import threading
import json
import time

class Peer:
    def __init__(self, host_addr, port_number, shared_directory):
        self.host_addr = host_addr
        self.port_number = port_number
        self.shared_directory = shared_directory
        self.peers = []
        self.shared_files = {}
    
    def start(self):
        server_thread = threading.Thread(target=self.run_server, daemon=True)
        server_thread.start()
    
    def run_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host_addr, self.port_number))
        server.listen(5)

        print(f"Peer is listening on {self.host_addr}, {self.port_number}")

        while True:
            conn, addr = server.accept()
            print(f"connection received from {addr}")

            thread = threading.Thread(target=self.handle_connection, args=(conn, addr), daemon=True)
            thread.start()

    def handle_connection(self, conn, addr):
        try:
            data = conn.recv(4096)

            if not data:
                return
            
            print(f"received message {data}")
            msg = json.loads(data.decode())
            msg_type = msg.get("type")

            if msg_type == "request":
                response = {
                    "type": "response", 
                    "message": "hello"
                }
                conn.send(json.dumps(response).encode())
                print("message sent")

        except json.JSONDecodeError:
            print("could not decode json object")
        
        except ConnectionError as e:
            print(f"Connection failed: {e}")
        except Exception as e:
            print(f"error: {e}")       
        finally:
            conn.close()
    
    def send_msg(self, addr, msg):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect(addr)
            data = json.dumps(msg).encode()
            sock.send(data)
            sock.close()
        
        except ConnectionError as e:
            print(f"Connection failed: {e}")
        except Exception as e:
            print(f"error: {e}")