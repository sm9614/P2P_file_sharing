from peer import Peer
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="The address of the peer")
    parser.add_argument("port", type=int, help="The port number of the peer")
    parser.add_argument(
        "dir",  help="The directory of files the peer can share")

    args = parser.parse_args()

    peer = Peer(args.host, args.port, args.dir)
    peer.start()
    peer.index_file()

    print("\nP2P commads:")
    print("-------------------------")
    print("Join <address> <port>")
    print("Search <filename>")
    print("Download <filename>")
    print("Get peers")
    print("Exit")
    print("-------------------------")

    while True:

        try:
            choice = input("\nchoice--> ")
            choice = choice.lower().strip().split()
            if choice[0] == "join":
                peer.join_network((choice[1], int(choice[2])))

            elif choice[0] == "search":
                peer.search_network(choice[1])

            elif choice[0] == "download":
                peer.download(choice[1])

            elif choice[0] == "get":
                print(peer.peers)

            elif choice[0] == "quit":
                break

            else:
                print("unknown command")

        except KeyboardInterrupt:
            break

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
