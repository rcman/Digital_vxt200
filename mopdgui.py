#!/usr/bin/env python3
import socket
import threading
import time
import logging
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# GUI imports
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog

# Configuration
CONFIG_DIR = Path.home() / ".mopd"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "mopd.log"
PID_FILE = CONFIG_DIR / "mopd.pid"

class MOPDaemon:
    def __init__(self, port=4343, host="0.0.0.0"):
        self.port = port
        self.host = host
        self.running = False
        self.socket = None
        self.clients = []
        self.load_config()
        
        # Setup logging
        if not CONFIG_DIR.exists():
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def load_config(self):
        """Load configuration from file"""
        defaults = {
            "port": 4343,
            "host": "0.0.0.0",
            "max_clients": 10,
            "welcome_message": "Welcome to MOP-D Service"
        }
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.port = config.get("port", defaults["port"])
                    self.host = config.get("host", defaults["host"])
                    self.max_clients = config.get("max_clients", defaults["max_clients"])
                    self.welcome_message = config.get("welcome_message", defaults["welcome_message"])
            except Exception as e:
                print(f"Error loading config: {e}")
                self.port = defaults["port"]
                self.host = defaults["host"]
                self.max_clients = defaults["max_clients"]
                self.welcome_message = defaults["welcome_message"]
        else:
            self.port = defaults["port"]
            self.host = defaults["host"]
            self.max_clients = defaults["max_clients"]
            self.welcome_message = defaults["welcome_message"]
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        config = {
            "port": self.port,
            "host": self.host,
            "max_clients": self.max_clients,
            "welcome_message": self.welcome_message
        }
        
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def handle_client(self, client_socket, address):
        """Handle incoming client connections"""
        self.clients.append((client_socket, address))
        logging.info(f"Connection from {address}, Total clients: {len(self.clients)}")
        
        try:
            client_socket.send(f"{self.welcome_message}\n".encode())
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode().strip()
                logging.info(f"Received from {address}: {message}")
                client_socket.send(b"Message received\n")
                
                # Broadcast to other clients
                for sock, addr in self.clients:
                    if sock != client_socket:
                        try:
                            sock.send(f"Broadcast from {address}: {message}\n".encode())
                        except:
                            self.clients.remove((sock, addr))
        except Exception as e:
            logging.error(f"Error handling client {address}: {e}")
        finally:
            if (client_socket, address) in self.clients:
                self.clients.remove((client_socket, address))
            client_socket.close()
            logging.info(f"Connection from {address} closed, Total clients: {len(self.clients)}")
    
    def start(self):
        """Start the MOP daemon"""
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(self.max_clients)
            logging.info(f"MOP-D started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    if len(self.clients) >= self.max_clients:
                        client_socket.send(b"Server is full, try again later\n")
                        client_socket.close()
                        continue
                        
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
            return False
        finally:
            if self.socket:
                self.socket.close()
        return True
    
    def stop(self):
        """Stop the MOP daemon"""
        self.running = False
        # Close all client connections
        for client_socket, address in self.clients:
            try:
                client_socket.close()
            except:
                pass
        self.clients.clear()
        
        if self.socket:
            self.socket.close()
        logging.info("MOP-D stopped")

class MOPDGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MOP-D Daemon Controller")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        self.daemon = MOPDaemon()
        self.daemon_thread = None
        self.is_running = False
        
        self.setup_gui()
        self.update_status()
    
    def setup_gui(self):
        # Create tabs
        tab_control = ttk.Notebook(self.root)
        
        # Control tab
        control_tab = ttk.Frame(tab_control)
        tab_control.add(control_tab, text='Control')
        
        # Log tab
        log_tab = ttk.Frame(tab_control)
        tab_control.add(log_tab, text='Log')
        
        # Config tab
        config_tab = ttk.Frame(tab_control)
        tab_control.add(config_tab, text='Configuration')
        
        tab_control.pack(expand=1, fill='both')
        
        # Control tab content
        control_frame = ttk.LabelFrame(control_tab, text="Daemon Control")
        control_frame.pack(padx=10, pady=10, fill='x')
        
        self.status_label = ttk.Label(control_frame, text="Status: Stopped")
        self.status_label.pack(pady=5)
        
        self.clients_label = ttk.Label(control_frame, text="Connected clients: 0")
        self.clients_label.pack(pady=5)
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Daemon", command=self.start_daemon)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop Daemon", command=self.stop_daemon, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        # Log tab content
        log_frame = ttk.LabelFrame(log_tab, text="Daemon Log")
        log_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled')
        self.log_text.pack(padx=5, pady=5, fill='both', expand=True)
        
        # Config tab content
        config_frame = ttk.LabelFrame(config_tab, text="Configuration Settings")
        config_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Port setting
        port_frame = ttk.Frame(config_frame)
        port_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(port_frame, text="Port:").pack(side='left')
        self.port_var = tk.IntVar(value=self.daemon.port)
        port_spinbox = ttk.Spinbox(port_frame, from_=1024, to=65535, textvariable=self.port_var, width=10)
        port_spinbox.pack(side='left', padx=5)
        
        # Host setting
        host_frame = ttk.Frame(config_frame)
        host_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(host_frame, text="Host:").pack(side='left')
        self.host_var = tk.StringVar(value=self.daemon.host)
        host_entry = ttk.Entry(host_frame, textvariable=self.host_var, width=20)
        host_entry.pack(side='left', padx=5)
        
        # Max clients setting
        max_clients_frame = ttk.Frame(config_frame)
        max_clients_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(max_clients_frame, text="Max Clients:").pack(side='left')
        self.max_clients_var = tk.IntVar(value=self.daemon.max_clients)
        max_clients_spinbox = ttk.Spinbox(max_clients_frame, from_=1, to=100, textvariable=self.max_clients_var, width=10)
        max_clients_spinbox.pack(side='left', padx=5)
        
        # Welcome message setting
        welcome_frame = ttk.Frame(config_frame)
        welcome_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(welcome_frame, text="Welcome Message:").pack(anchor='w')
        self.welcome_var = tk.StringVar(value=self.daemon.welcome_message)
        welcome_entry = ttk.Entry(welcome_frame, textvariable=self.welcome_var, width=50)
        welcome_entry.pack(fill='x', padx=5, pady=2)
        
        # Save config button
        save_btn = ttk.Button(config_frame, text="Save Configuration", command=self.save_config)
        save_btn.pack(pady=10)
        
        # Set up log monitoring
        self.update_log()
    
    def save_config(self):
        self.daemon.port = self.port_var.get()
        self.daemon.host = self.host_var.get()
        self.daemon.max_clients = self.max_clients_var.get()
        self.daemon.welcome_message = self.welcome_var.get()
        self.daemon.save_config()
        messagebox.showinfo("Success", "Configuration saved successfully!")
    
    def start_daemon(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Daemon is already running!")
            return
        
        # Update config from UI
        self.daemon.port = self.port_var.get()
        self.daemon.host = self.host_var.get()
        self.daemon.max_clients = self.max_clients_var.get()
        self.daemon.welcome_message = self.welcome_var.get()
        
        self.daemon_thread = threading.Thread(target=self.run_daemon)
        self.daemon_thread.daemon = True
        self.daemon_thread.start()
        
        # Wait a moment for the daemon to start
        self.root.after(500, self.check_daemon_started)
    
    def run_daemon(self):
        self.is_running = self.daemon.start()
    
    def check_daemon_started(self):
        if self.is_running:
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_label.config(text="Status: Running")
        else:
            messagebox.showerror("Error", "Failed to start daemon. Check the log for details.")
    
    def stop_daemon(self):
        if not self.is_running:
            return
        
        self.daemon.stop()
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Status: Stopped")
        self.clients_label.config(text="Connected clients: 0")
    
    def update_status(self):
        if self.is_running:
            self.clients_label.config(text=f"Connected clients: {len(self.daemon.clients)}")
        self.root.after(1000, self.update_status)
    
    def update_log(self):
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, 'r') as f:
                    content = f.read()
                
                self.log_text.config(state='normal')
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, content)
                self.log_text.see(tk.END)
                self.log_text.config(state='disabled')
            except Exception as e:
                print(f"Error reading log file: {e}")
        
        self.root.after(2000, self.update_log)

def main():
    root = tk.Tk()
    app = MOPDGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_daemon(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    # Check if running as root for privileged ports
    if len(sys.argv) > 1 and sys.argv[1] == "--root-warning":
        if os.geteuid() == 0:
            print("Warning: Running GUI applications as root is not recommended.")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                sys.exit(0)
    
    main()