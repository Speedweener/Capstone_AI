# Script to be put in the bluetooth gateway to facilitate mission of sensor packets to Ultra96
# Main Features: Tunneling and socket programming

from time import sleep
import sshtunnel
import logging
import struct
import socket
from config_loader import load_config_from_dot_env
import sys
from redis_queue.redis_queue import get_task_queue


CONFIG = load_config_from_dot_env()
SSH_PORT = 22
print(CONFIG)
# For sunfire
SUNFIRE_HOST = CONFIG["SUNFIRE_HOST"]
SUNFIRE_USERNAME = CONFIG["SUNFIRE_USERNAME"]
SUNFIRE_PASSWORD = CONFIG["SUNFIRE_PASSWORD"]

# For Ultra96
ULTRA_HOST = CONFIG["ULTRA_HOST"]
ULTRA_USERNAME = CONFIG["ULTRA_USERNAME"]
ULTRA_PASSWORD = CONFIG["ULTRA_PASSWORD"]
ULTRA_PORT = 2106 

# For Localhost
LOCAL_HOST = "localhost"
LOCAL_BINDING_ADDRESS = "127.0.0.1"
LOCAL_PORT = 12345

# For Logging
LOG_FILENAME = "gateway_brain.log"


class GatewayBrain:
    def __init__(self):
        # Init logging
        logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, filemode='w',
                            format='%(asctime)s:%(levelname)s:%(message)s')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # Init tunnelling
        success = self.tunnel_to_Ultra96()

        if not success:
            self.log_and_print(
                "[ERROR] Gateway brain has failed tunneling. Executing shutdown.")
            quit()

        self.U96_socket = self.connect_and_bind_socket()
        self.log_and_print("[CONNECTION] Connection established to Ultra96.")

        # Message buffers
        self.ultra_queue = []

    # Function to tunnel to Ultra96
    # Returns True if successful, else returns False
    def tunnel_to_Ultra96(self):

        sunfire_tunnel = sshtunnel.open_tunnel(
            (SUNFIRE_HOST, SSH_PORT),
            remote_bind_address=(ULTRA_HOST, SSH_PORT),
            ssh_username=SUNFIRE_USERNAME,
            ssh_password=SUNFIRE_PASSWORD,
            block_on_close=False
        )
        try:
            sunfire_tunnel.start()
            self.log_and_print("[CONNECTION] Sunfire Tunnel opened.")
        except sshtunnel.BaseSSHTunnelForwarderError:
            self.log_and_print(
                "[ERROR] Sunfire Tunnel has encountered issues.")
            return False  # on tunnelling failure
        print(sunfire_tunnel.local_bind_port)
        xilinx_tunnel = sshtunnel.open_tunnel(
            ssh_address_or_host=(
                LOCAL_HOST, sunfire_tunnel.local_bind_port),  # ssh into xilinx
            remote_bind_address=(LOCAL_BINDING_ADDRESS,
                                 ULTRA_PORT),  # binds xilinx host
            ssh_username=ULTRA_USERNAME,
            ssh_password=ULTRA_PASSWORD,
            # localhost to bind it to
            local_bind_address=(LOCAL_BINDING_ADDRESS, LOCAL_PORT),
            block_on_close=False
        )
        try:
            xilinx_tunnel.start()
            self.log_and_print("[CONNECTION] Xilinx Tunnel opened.")
        except sshtunnel.BaseSSHTunnelForwarderError:
            self.log_and_print("[ERROR] Xilinx Tunnel has encountered issues.")
            return False  # on tunnelling failure

        return True  # on tunnelling success

    # Creates and bind socket over tunneling
    def connect_and_bind_socket(self):
        ultra96_socket = socket.socket()
        ultra96_socket.connect((LOCAL_BINDING_ADDRESS, LOCAL_PORT))
        self.log_and_print(
            "[CONNECTION] Socket to Ultra96 connected successfully.")
        return ultra96_socket

    # Send message over the socket to the Ultra96
    # message should be of a bytes like object
    def send_to_Ultra(self, message, to_plot = False):
        try:
            
            self.U96_socket.sendall(message)
            formatStr = "<" + "b"*len(message)
            msg = struct.unpack(formatStr, message)
            # For serial plotter
            if to_plot:
                get_task_queue().enqueue(*(msg[1:]))
            self.log_and_print(f"[TO ULTRA] Message sent to Ultra96: {msg}")
        except socket.error:  # disconnected or something
            sleep(0.1)  # Wait for reconnection, to be done by the listener loop

    # Infinite loop to listen over the socket
    # Meant to be used with threading
    # Create a daemon thread to listen
    def listen_to_ultra_loop(self):
        while True:
            message = self.U96_socket.recv(2048)  # Returns len 0 if disconnected
            if message:
                self.ultra_queue.append(message)
                try:
                    msg = message
                    self.log_and_print(f"[FROM ULTRA] Message received: {msg}")
                except:
                    print("no.")
            else:  # ultra96 disconnected disconnected, attempt reconnect
                self.log_and_print("[ERROR] Disconnected from Ultra96. Attempting Reconnection...")
                self.U96_socket.connect((LOCAL_BINDING_ADDRESS, LOCAL_PORT))
                self.log_and_print("[CONNECTION] Reconnected to Eval Server.")

    # Terminate Gateway
    def terminate(self):
        self.log_and_print("[CONNECTION] Gateway closing.")
        quit()

    # Logs and prints the messages
    def log_and_print(self, message):
        self.logger.debug(message)
        # print(message)
