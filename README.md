# P2P_file_sharing
```
Created a peer to peer file sharing program. The each peer runs as its own thread and uses TCP to accept connections.
Files are transferred in chunks and reassembled. The downloaded file's hash is compared to the orignal files hash to verify integrity.
The network uses a bootstrap peer to act as a gateway for new peers to join the network.

Running the code:
  1. Create a venv using python -m venv /path/to/new/virtual/environment
  2. Activate the venv using .\venv\Scripts\activate.bat
  3. Install the requirements using pip install -r requirements.txt
  4. run the code with through the terminal via python program.py <host> <port> <dir>
  5. Each peer needs to run on a seperate terminal window and needs to join the network via join <boostrap_host> <bootstrap_port>
  6. Enter one of the following commands:
    Join <address> <port>
    Search <filename>
    Download <filename>
    Get peers
    Exit


usage: program.py [-h] host port dir
```
