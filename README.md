# Peer-to-Peer Communication Application

This is a Python-based Peer-to-Peer (P2P) communication system designed for local network environments. It supports real-time messaging, peer discovery, file and directory transfers, and manual peer management through a graphical user interface.

## Features

- Peer discovery using UDP broadcasting
- Broadcast and private messaging between peers
- File sharing with individual or all peers
- Directory sharing with structure preservation
- Manual addition of peers via IP and port
- GUI interface built with Tkinter
- Concurrent handling of multiple peers using threading
- Progress display during file transfers using `tqdm`

## Technologies Used

- Python
- `socket` (TCP and UDP communication)
- `threading` (for concurrent connections)
- `tkinter` (for GUI development)
- `tqdm` (to show file transfer progress)
- `os` (for file and directory operations)


## Getting Started

1. Clone this repository or download the ZIP.
2. Make sure Python 3 is installed on your system.
3. Open multiple terminal windows or systems to simulate multiple peers.
4. Run the script:

    ```bash
   python main.py
