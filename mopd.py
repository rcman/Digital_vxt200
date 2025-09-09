#!/usr/bin/env python3
import socket
import threading
import time
import logging
from daemon import DaemonContext
import pidfile

# Configuration
LISTEN_PORT = 4343
LOG_FILE = '/var/log/mopd.log'
PID_FILE = '/var/run/mopd.pid'

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MOPDaemon:
    def __init__(self, port=LISTEN_PORT):
        self.port = port
        self.running = False
        self.socket = None

    def handle_client(self, client_socket, address):
        """Handle incoming client connections"""
        logging.info(f"Connection from {address}")
        try:
            client_socket.send(b"Welcome to MOP-D Service\n")
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                logging.info(f"Received from {address}: {data.decode().strip()}")
                client_socket.send(b"Message received\n")
        except Exception as e:
            logging.error(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            logging.info(f"Connection from {address} closed")

    def start(self):
        """Start the MOP daemon"""
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.listen(5)
            logging.info(f"MOP-D started on port {self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        logging.error(f"Error accepting connection: {e}")
        except Exception as e:
            logging.error(f"Failed to start MOP-D: {e}")
        finally:
            if self.socket:
                self.socket.close()

    def stop(self):
        """Stop the MOP daemon"""
        self.running = False
        if self.socket:
            self.socket.close()

def run_daemon():
    daemon = MOPDaemon()
    with DaemonContext(
        pidfile=pidfile.PIDLockFile(PID_FILE),
        umask=0o002,
        working_directory='/tmp'
    ):
        daemon.start()

if __name__ == "__main__":
    run_daemon()