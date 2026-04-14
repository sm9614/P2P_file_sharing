from peer import Peer
import time


def main():
    peer1 = Peer(host_addr="127.0.0.1", port_number=8080, shared_directory="/")
    peer1.start()

    peer2 = Peer(host_addr="127.0.0.1", port_number=8081, shared_directory="/")
    peer2.start()

    peer3 = Peer(host_addr="127.0.0.1", port_number=8082, shared_directory="/")
    peer3.start()

    time.sleep(1)

    print("\nPeer 2 joining the network\n")

    join_msg = {
        "type": "join",
        "address": "127.0.0.1",
        "port_number": 8081
    }

    peer2.send_msg(addr=("127.0.0.1", 8080), msg=join_msg)
    time.sleep(1)

    print("\nPeer 3 joining the network\n")

    join_msg = {
        "type": "join",
        "address": "127.0.0.1",
        "port_number": 8082
    }

    peer3.send_msg(addr=("127.0.0.1", 8080), msg=join_msg)
    time.sleep(1)

    print("\nPeer 2 requesting peer list from the network\n")

    get_peers_msg = {
        "type": "get_peers"
    }

    peer2.send_msg(addr=("127.0.0.1", 8080), msg=get_peers_msg)

    time.sleep(3)


if __name__ == "__main__":
    main()
