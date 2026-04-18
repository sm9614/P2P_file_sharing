from pathlib import Path
import socket
import threading
import json
import math
import hashlib


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
                with open(file, "rb") as f:
                    file_hash = hashlib.file_digest(f, "sha256").hexdigest()

                self.shared_files[file.name] = {
                    "path": str(file),
                    "size": size,
                    "chunks": chunks,
                    "hash": file_hash
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

    def join_network(self, bootstrap_addr):
        join_msg = {
            "type": "join",
            "address": self.host_addr,
            "port_number": self.port_number
        }

        response = self.send_msg(bootstrap_addr, join_msg)

        if response and response.get("type") == "join_ack":
            with self.lock:
                for peer in response.get("peers", []):
                    if tuple(peer) not in self.peers:
                        self.peers.append(tuple(peer))
            print("joined successfully")
        else:
            print("unable to join network")

        for peer in self.peers:
            if tuple(peer) == (self.host_addr, self.port_number):
                continue

            if tuple(peer) == bootstrap_addr:
                continue

            self.send_msg(tuple(peer), join_msg)

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
                "chunks": file_info["chunks"],
                "hash": file_info["hash"]
            }

        else:
            response = {
                "type": "search_response",
                "exists": False,
            }
        conn.send(json.dumps(response).encode())

    def search_network(self, filename):
        found = False
        for peer in self.peers:
            if peer == (self.host_addr, self.port_number):
                continue

            search_msg = {
                "type": "search",
                "filename": filename
            }

            response = self.send_msg(peer, search_msg)

            if response and response.get("exists"):
                found = True
                print(f"Found {filename} on peer {peer}" )
        if not found:
            print(f"Could not find {filename} on any peers")

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

    def download(self, filename):
        for peer in self.peers:
            if peer == (self.host_addr, self.port_number):
                continue

            search_msg = {
                "type": "search",
                "filename": filename
            }

            response = self.send_msg(peer, search_msg)

            if not response or not response.get("exists"):
                continue

            chunks = response.get("chunks")
            original_hash = response.get("hash")

            print(f"Downloading {filename} from {peer}")
            print(f"Total chunks: {chunks}")

            file_data = bytearray()

            for i in range(chunks):
                chunk_msg = {
                    "type": "request_chunk",
                    "filename": filename,
                    "chunk_index": i,
                }

                response = self.send_msg(peer, chunk_msg)

                if not response or not response.get("exists") or "data" not in response:
                    print(f"Failed to get chunk {i}")
                    return

                try:
                    data = bytes.fromhex(response["data"])

                except Exception:
                    print(f"Failed to decode chunk {i}")
                    return

                file_data.extend(data)

            path = Path(self.shared_directory)/filename

            with open(path, "wb") as f:
                f.write(file_data)

            with open(path, "rb") as f:
                file_hash = hashlib.file_digest(f, "sha256").hexdigest()

            if original_hash != file_hash:
                print("Hash does not match, deleting file")
                path.unlink(missing_ok=True)
                return

            print("File downloaded successfully")
            self.index_file()
            return
        print("file not found")
