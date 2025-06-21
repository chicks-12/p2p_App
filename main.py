import os
import socket
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog

# Shared list to store connected peers
peers = []  # Format: [(ip, port), ...]

# Predefined broadcast port
BROADCAST_PORT = 9090

# Function to handle incoming peer connections
def start_peer_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connected to peer: {client_address}")
        if client_address not in peers:
            peers.append(client_address)
        threading.Thread(target=handle_incoming_connections, args=(client_socket,)).start()

# Function to handle incoming messages
def handle_incoming_connections(peer_socket):
    while True:
        try:
            message = peer_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Message from peer: {message}")
            update_peer_list()
            display_message(f"Received: {message}")
        except ConnectionResetError:
            print("A peer has disconnected.")
            break

# Function to handle broadcasting presence
def start_peer_discovery(host, port):
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = f"{host}:{port}"  # Send your address for discovery

    while True:
        broadcast_socket.sendto(message.encode('utf-8'), ('<broadcast>', BROADCAST_PORT))
        threading.Event().wait(5)  # Broadcast every 5 seconds

# Function to send a message to all peers
def send_message_to_all_peers(message):
    for peer in peers:
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect(peer)
            peer_socket.send(message.encode('utf-8'))
            peer_socket.close()
            display_message(f"Sent to {peer}: {message}")
        except Exception as e:
            print(f"Failed to send message to {peer}: {e}")

# Function to send a private message to a specific peer
def send_private_message(target_peer, message):
    try:
        private_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        private_socket.connect(target_peer)
        private_socket.send(message.encode('utf-8'))
        private_socket.close()
        print(f"Message sent to {target_peer}")
        display_message(f"Sent to {target_peer}: {message}")
    except Exception as e:
        print(f"Failed to send private message to {target_peer}: {e}")

# Function to send a file to all peers
def send_file_to_all_peers(file_path):
    for peer in peers:
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect(peer)
            peer_socket.send(b'FILE')  # Send a header indicating file transfer
            peer_socket.send(os.path.basename(file_path).encode('utf-8'))  # Send file name
            with open(file_path, 'rb') as file:
                data = file.read(1024)
                while data:
                    peer_socket.send(data)
                    data = file.read(1024)
            peer_socket.close()
            display_message(f"File sent to {peer}: {file_path}")
        except Exception as e:
            print(f"Failed to send file to {peer}: {e}")

# Function to send a directory to a specific peer
def send_directory_to_peer(target_peer, directory_path):
    try:
        private_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        private_socket.connect(target_peer)
        private_socket.send(b'DIRECTORY')  # Send a header indicating directory transfer
        for root, dirs, files in os.walk(directory_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                private_socket.send(os.path.relpath(file_path, directory_path).encode('utf-8'))  # Send relative file path
                with open(file_path, 'rb') as file:
                    data = file.read(1024)
                    while data:
                        private_socket.send(data)
                        data = file.read(1024)
        private_socket.close()
        print(f"Directory sent to {target_peer}")
        display_message(f"Directory sent to {target_peer}: {directory_path}")
    except Exception as e:
        print(f"Failed to send directory to {target_peer}: {e}")

# Function to listen for broadcast messages
def listen_for_broadcasts(host, port):
    listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener_socket.bind(('', BROADCAST_PORT))
    print(f"Listening for broadcasts on port {BROADCAST_PORT}")

    while True:
        message, address = listener_socket.recvfrom(1024)
        peer_ip, peer_port = message.decode('utf-8').split(':')
        peer_port = int(peer_port)
        peer_address = (peer_ip, peer_port)

        if peer_address != (host, port) and peer_address not in peers:
            peers.append(peer_address)
            print(f"Discovered peer: {peer_address}")
            send_message_to_all_peers(f"New peer discovered: {peer_address}")
            update_peer_list()

# Update peer list in GUI
def update_peer_list():
    peer_listbox.delete(0, tk.END)
    for peer in peers:
        peer_listbox.insert(tk.END, f"{peer[0]}:{peer[1]}")

# GUI for displaying messages
def display_message(message):
    message_listbox.insert(tk.END, message)
    message_listbox.yview(tk.END)

# GUI for sending files to all peers
def send_file_to_all():
    file_path = filedialog.askopenfilename()
    if file_path:
        send_file_to_all_peers(file_path)
        messagebox.showinfo("File Transfer", "File sent to all peers.")
    else:
        messagebox.showwarning("Warning", "No file selected.")

# GUI for sending a directory to a specific peer
def send_directory():
    try:
        selected_peer = peer_listbox.curselection()[0]
        target_peer = peers[selected_peer]
        directory_path = filedialog.askdirectory()
        if directory_path:
            send_directory_to_peer(target_peer, directory_path)
            messagebox.showinfo("Directory Transfer", f"Directory sent to {target_peer}.")
        else:
            messagebox.showwarning("Warning", "No directory selected.")
    except IndexError:
        messagebox.showwarning("Warning", "Please select a peer to send the directory.")

# Send message to all peers
def send_to_all():
    message = message_entry.get()
    if message:
        send_message_to_all_peers(message)
        messagebox.showinfo("Message", "Message sent to all peers.")
    else:
        messagebox.showwarning("Warning", "Please enter a message.")

# Send private message
def send_private():
    try:
        selected_peer = peer_listbox.curselection()[0]
        target_peer = peers[selected_peer]
        message = message_entry.get()
        if message:
            send_private_message(target_peer, message)
            messagebox.showinfo("Message", f"Message sent to {target_peer}.")
        else:
            messagebox.showwarning("Warning", "Please enter a message.")
    except IndexError:
        messagebox.showwarning("Warning", "Please select a peer to message.")

# Function to manually add a peer
def add_peer_manually():
    try:
        target_host = simpledialog.askstring("Manual Peer Entry", "Enter peer's IP:")
        target_port = int(simpledialog.askstring("Manual Peer Entry", "Enter peer's port:"))
        peer_socket = connect_to_peer(target_host, target_port)
        if peer_socket:
            update_peer_list()
        else:
            messagebox.showerror("Error", f"Failed to add peer {target_host}:{target_port}.")
    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter a valid IP address and port.")

# Function to connect to a peer
# Function to connect to a peer
def connect_to_peer(target_host, target_port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((target_host, target_port))
        peers.append((target_host, target_port))
        threading.Thread(target=handle_incoming_connections, args=(client_socket,)).start()
        print(f"Connected to peer: {target_host}:{target_port}")
        return client_socket
    except Exception as e:
        print(f"Failed to connect to peer {target_host}:{target_port}: {e}")
        return None

# Main function to integrate all modules
def main():
    host = simpledialog.askstring("Enter Your IP", "Enter your IP (localhost for local testing):")
    port = int(simpledialog.askstring("Enter Your Port", "Enter your port:"))

    # Start the peer server
    threading.Thread(target=start_peer_server, args=(host, port), daemon=True).start()

    # Start the broadcast discovery
    threading.Thread(target=start_peer_discovery, args=(host, port), daemon=True).start()

    # Start listening for broadcasts
    threading.Thread(target=listen_for_broadcasts, args=(host, port), daemon=True).start()

    # GUI setup
    window = tk.Tk()
    window.title("Peer-to-Peer Communication")
    window.geometry("600x500")
    window.config(bg='#2c3e50')  # Navy blue background

    # Chat messages display
    global message_listbox
    message_listbox = tk.Listbox(window, width=80, height=15, bg='#34495e', fg='white')
    message_listbox.pack(pady=10)

    # Create message entry field
    global message_entry
    message_label = tk.Label(window, text="Message:", fg='white', bg='#2c3e50')
    message_label.pack(pady=5)
    message_entry = tk.Entry(window, width=60, bg='#34495e', fg='white')
    message_entry.pack(pady=10)

    # Buttons for sending messages and files
    button_frame = tk.Frame(window, bg='#2c3e50')
    button_frame.pack(pady=5)

    send_all_button = tk.Button(button_frame, text="Send to All", command=send_to_all, bg='#16a085', fg='white', width=15)
    send_all_button.grid(row=0, column=0, padx=5)

    send_private_button = tk.Button(button_frame, text="Send Private", command=send_private, bg='#16a085', fg='white', width=15)
    send_private_button.grid(row=0, column=1, padx=5)

    send_file_button = tk.Button(button_frame, text="Send File to All", command=send_file_to_all, bg='#16a085', fg='white', width=15)
    send_file_button.grid(row=1, column=0, pady=5, padx=5)

    send_directory_button = tk.Button(button_frame, text="Send Directory", command=send_directory, bg='#16a085', fg='white', width=15)
    send_directory_button.grid(row=1, column=1, pady=5, padx=5)

    # Peer list display
    peer_list_label = tk.Label(window, text="Connected Peers:", fg='white', bg='#2c3e50')
    peer_list_label.pack(pady=5)
    global peer_listbox
    peer_listbox = tk.Listbox(window, width=50, height=10, bg='#34495e', fg='white')
    peer_listbox.pack(pady=10)

    # Button to add peers manually
    add_peer_button = tk.Button(window, text="Add Peer Manually", command=add_peer_manually, bg='#e67e22', fg='white', width=20)
    add_peer_button.pack(pady=5)

    window.mainloop()

# Run the main function to start the application
if __name__ == "__main__":
    main()
