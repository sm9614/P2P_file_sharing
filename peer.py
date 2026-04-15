from pathlib import Path
import socket
import threading
import json
import math


class Peer:


    def __init__(self, host_addr, port_number, shared_directory):
        self.host_addr = host_addr
        self.port_number = port_number
        self.shared_directory = shared_directory
        self.peers = [(self.host_addr, self.port_number)]
        self.shared_files = {}
        self.lock = threading.Lock()

    def start(self):
        server_thread = threading.Thread(target=self.run_server, daemon=True)
        server_thread.start()

    def run_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host_addr, self.port_number))
        server.listen(5)

        print(f"\nPeer is listening on {self.host_addr}, {self.port_number}")

        while True:
            conn, addr = server.accept()
            print(f"connection received from {addr}")

            thread = threading.Thread(
                target=self.handle_connection, args=(conn, addr), daemon=True)
            thread.start()

    def index_file(self):
        shared_path = Path(self.shared_directory)

        for file in shared_path.iterdir():

            if file.is_file():
                size = file.stat().st_size
                chunks = math.ceil(size / 1024)

                self.shared_files[file.name] = {
                    "path": str(file),
                    "size": size,
                    "chunks": chunks
                }
        print(f"indexed files: {self.shared_files}")
    
    def join(self, conn, msg):
        peer = (msg.get("address"), msg.get("port_number"))

        with self.lock:
            if peer not in self.peers:
                self.peers.append(peer)

            response = {
                "type": "join_ack",
                "peers": self.peers
            }
        conn.send(json.dumps(response).encode())
    
    def get_peers(self, conn):
        with self.lock:
            peers = list(self.peers)

        response = {
            "type": "peer_ack",
            "peers": peers
        }
        conn.send(json.dumps(response).encode())
    
    def search(self, conn, msg):
        filename = msg.get("filename")

        with self.lock:
            file_info = self.shared_files.get(filename)

        if file_info:
            response = {
                "type": "search_response",
                "exists": True,
                "size": file_info["size"],
                "chunks": file_info["chunks"]
            }

        else:
            response = {
                "type": "search_response",
                "exists": False,
            }
        conn.send(json.dumps(response).encode())
    
    def request_chunk(self, conn, msg):
        filename = msg.get("filename")
        chunk_idx = msg.get("chunk_index")

        with self.lock:
            file_info = self.shared_files.get(filename)

        if not file_info:
            response = {
                "type": "chunk_response",
                "exists": False,
            }
        else:
            try:
                path = file_info.get("path")
                with open(path, "rb") as file:
                    file.seek(chunk_idx * 1024)
                    chunk = file.read(1024)
                response = {
                    "type": "chunk_response",
                    "exists": True,
                    "chunk_index": chunk_idx,
                    "data": chunk.hex() 
                }
            except FileNotFoundError:
                print("file not found")
            except Exception as e:
                print(f"error: {e}")
        
        conn.send(json.dumps(response).encode())
                


    def handle_connection(self, conn, addr):
        try:
            data = conn.recv(4096)

            if not data:
                return

            print(f"received message {data}")
            msg = json.loads(data.decode())
            msg_type = msg.get("type")

            if msg_type == "join":
                self.join(conn, msg)

            elif msg_type == "get_peers":
                self.get_peers(conn)

            elif msg_type == "search":
                self.search(conn, msg)

            elif msg_type == "request_chunk":
                self.request_chunk(conn, msg)

            elif msg_type == "ping":
                pass
            else:
                print(f"unknow message type: {msg_type}")

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
            response = sock.recv(4096)

            if response:
                return json.loads(response.decode())

        except ConnectionError as e:
            print(f"Connection failed: {e}")
        except Exception as e:
            print(f"error: {e}")
        finally:
            sock.close()
