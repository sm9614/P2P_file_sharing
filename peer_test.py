from peer import Peer
import time


def main():
    peer1 = Peer(host_addr="127.0.0.1", port_number=8080, shared_directory="./shared1")
    peer2 = Peer(host_addr="127.0.0.1", port_number=8081, shared_directory="./shared2")
    peer3 = Peer(host_addr="127.0.0.1", port_number=8082, shared_directory="./shared3")
    
    peer1.start()
    peer2.start()
    peer3.start()

    peer1.index_file()
    peer2.index_file()
    peer3.index_file()

    time.sleep(1)

    print("\nPeer 2 joining the network\n")

    join_msg = {
        "type": "join",
        "address": "127.0.0.1",
        "port_number": 8081
    }

    response = peer2.send_msg(addr=("127.0.0.1", 8080), msg=join_msg)
    print(f"join response: {response}")
    time.sleep(1)

    print("\nPeer 3 joining the network\n")

    join_msg = {
        "type": "join",
        "address": "127.0.0.1",
        "port_number": 8082
    }

    response = peer3.send_msg(addr=("127.0.0.1", 8080), msg=join_msg)
    print(f"join response: {response}")
    time.sleep(1)

    print("\nPeer 2 searching for file\n")
    search_msg = {
        "type": "search",
        "filename": "test.txt"
    }

    response = peer2.send_msg(addr=("127.0.0.1", 8080), msg=search_msg)
    print(f"search response: {response}")

    print("\nPeer 2 requesting chunk\n")
    chunk_msg = {
        "type": "request_chunk",
        "filename": "test.txt",
        "chunk_index": 0
    }

    response = peer2.send_msg(addr=("127.0.0.1", 8080), msg=chunk_msg)
    print(f"chunk response: {response}")

    print("\nPeer 2 requesting peer list from the network\n")

    get_peers_msg = {
        "type": "get_peers"
    }

    response = peer2.send_msg(addr=("127.0.0.1", 8080), msg=get_peers_msg)
    print(f"get peers response: {response}")

    time.sleep(3)


if __name__ == "__main__":
    main()
