#!/usr/bin/env python3

import os
import sys
import argparse
import logging
from logging.handlers import SysLogHandler
from scapy.all import sniff, Ether, MOP
from scapy.all import __version__ as scapy_version

# --- Global Configuration ---
VERSION = "1.0"
MOP_FILE_PATH = "/usr/local/mop"  # Default MOP directory path
# This can be configured in your system's syslog configuration
LOG_FACILITY = SysLogHandler.LOG_DAEMON

# --- Placeholder Functions from C Code ---
# In a real implementation, you would replace these with actual logic.
# The C code's functions like deviceInitAll(), mopProcessDL(), etc.,
# would be complex, and these are simplified stubs for demonstration.

class InterfaceInfo:
    """A conceptual class to hold interface information."""
    def __init__(self, name, eaddr):
        self.name = name
        self.eaddr = eaddr

def mop_cmp_eaddr(addr1, addr2):
    """Compares two Ethernet addresses."""
    return addr1 != addr2

def mop_process_dl(iface, pkt):
    """Placeholder for MOP Dump/Load processing."""
    print(f"Processing MOP Dump/Load packet on {iface.name}")

def mop_process_rc(iface, pkt):
    """Placeholder for MOP Remote Console processing."""
    print(f"Processing MOP Remote Console packet on {iface.name}")

# --- Core Packet Processing ---

def mop_process_packet(iface_info, packet):
    """
    Processes an incoming MOP packet.
    This function mimics the mopProcess() function in the C code.
    """
    # Check if the packet is a MOP packet
    if not packet.haslayer(MOP):
        return

    # Ignore our own transmissions by checking the source MAC address
    if not mop_cmp_eaddr(iface_info.eaddr, packet.src):
        return

    mop_layer = packet.getlayer(MOP)

    # Check for MOP V3 or V4 messages based on the protocol type
    if (mop_layer.type == "MOP_K_PROTO_DL" and args.not_v3):
        return
    if (mop_layer.type == "MOP_K_PROTO_RC" and args.not_v4):
        return

    if mop_layer.type == "MOP_K_PROTO_DL":
        mop_process_dl(iface_info, packet)
    elif mop_layer.type == "MOP_K_PROTO_RC":
        mop_process_rc(iface_info, packet)
    else:
        # Ignore other MOP types
        pass

# --- Main Function and Argument Parsing ---

def main():
    """
    Main function to parse arguments and start the MOP daemon.
    This function mimics the main() function in the C code.
    """
    global args

    parser = argparse.ArgumentParser(
        description="MOP Dump/Load Daemon",
        usage="%(prog)s -a [-d -f -v] [-3 | -4]\n"
              "       %(prog)s [-d -f -v] [-3 | -4] interface [...]"
    )
    parser.add_argument("-3", dest="not_v3", action="store_true",
                        help="Do not process MOP V3 messages")
    parser.add_argument("-4", dest="not_v4", action="store_true",
                        help="Do not process MOP V4 messages")
    parser.add_argument("-a", dest="all", action="store_true",
                        help="Listen on all interfaces")
    parser.add_argument("-d", dest="debug", action="store_true",
                        help="Print debugging messages")
    parser.add_argument("-f", dest="foreground", action="store_true",
                        help="Run in the foreground")
    parser.add_argument("-s", dest="mop_dir", default=MOP_FILE_PATH,
                        help="Path to the MOP directory")
    parser.add_argument("-v", dest="version", action="store_true",
                        help="Print version information and exit")
    parser.add_argument("interfaces", nargs="*",
                        help="Interface(s) to listen on")

    args = parser.parse_args()

    if args.version:
        print(f"{parser.prog}: version {VERSION}")
        sys.exit(0)

    # Validate command-line arguments
    if (args.all and args.interfaces) or (not args.all and not args.interfaces) or (args.not_v3 and args.not_v4):
        parser.error("Incorrect usage. See --help for details.")

    # Set up logging to syslog
    try:
        handler = SysLogHandler(address="/dev/log", facility=LOG_FACILITY)
        logging.basicConfig(level=logging.INFO, handlers=[handler],
                            format='%(name)s: %(message)s')
        syslog = logging.getLogger("mopd")
    except Exception as e:
        syslog = logging.getLogger("mopd")
        syslog.error(f"Could not open syslog: {e}. Logging to stderr instead.")
        logging.basicConfig(level=logging.INFO,
                            format='%(name)s: %(message)s')
        
    if not args.foreground and not args.debug:
        # Forking into a daemon process. Note that this is a simplified
        # version and a proper daemon library would be better.
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit parent process
        except OSError as e:
            syslog.error(f"Cannot fork: {e}")
            sys.exit(1)

        # It's good practice to redirect standard file descriptors in a daemon
        os.setsid()
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()
        
    syslog.info(f"{parser.prog} {VERSION} started.")
    
    # --- Packet Sniffing Loop ---
    
    # Placeholder for device initialization. In a real scenario, this
    # would discover interfaces and their MAC addresses.
    # For this example, we'll create a dummy interface info object.
    
    if args.all:
        print("Starting MOP daemon on all interfaces...")
        # Get a list of all active network interfaces
        interfaces_to_sniff = [iface.name for iface in os.scandir('/sys/class/net') if iface.is_dir() and iface.name != 'lo']
    else:
        interfaces_to_sniff = args.interfaces
        print(f"Starting MOP daemon on interfaces: {', '.join(interfaces_to_sniff)}")

    # Create dummy interface info for demonstration
    iface_info = InterfaceInfo("eth0", "00:00:00:00:00:00")
    
    # Scapy's sniff function is the equivalent of the C code's main loop
    # that "selects" on descriptors.
    print("Sniffing packets... Press Ctrl+C to stop.")
    sniff(iface=interfaces_to_sniff, prn=lambda pkt: mop_process_packet(iface_info, pkt), store=0)

if __name__ == "__main__":
    main()
