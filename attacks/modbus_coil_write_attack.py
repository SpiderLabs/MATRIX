from pymodbus.client import ModbusTcpClient
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class ModbusUnauthorizedCoilWriter:
    def __init__(self, host='localhost', port=502):
        self.host = host
        self.port = port
        self.client = None

    def connect(self):
        """Establish connection to Modbus server"""
        try:
            self.client = ModbusTcpClient(self.host, port=self.port)
            if self.client.connect():
                logger.info(f"Connected to target Modbus server at {self.host}:{self.port}")
                return True
            return False
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def write_coils(self, start_addr=0):
        """Write coil values: First 4 ON, Last 4 OFF"""
        values = [True] * 4 + [False] * 4
        try:
            result = self.client.write_coils(start_addr, values)
            if not result.isError():
                logger.info("Successfully wrote coil values.")
            else:
                logger.error("Failed to write coil values.")
        except Exception as e:
            logger.error(f"Error writing coils: {e}")

    def read_coils(self, start_addr=0, count=8):
        """Read coil status (binary outputs)"""
        try:
            result = self.client.read_coils(address=start_addr, count=count)
            if not result.isError():
                logger.info("Coil Status:")
                for i, value in enumerate(result.bits):
                    status = "ON" if value else "OFF"
                    logger.info("  Coil {}: {}".format(start_addr + i, status))
            return result.bits
        except Exception as e:
            logger.error(f"Failed to read coils: {e}")
            return None

    def run_test(self):
        """Write values to coils and then read them back."""
        if self.connect():
            logger.info("\nWriting values to Modbus server...")
            self.write_coils()
            
            time.sleep(0.5)  # Small delay before reading
            
            logger.info("\nReading values back...")
            self.read_coils()
            
            self.client.close()
        else:
            logger.error("Failed to connect to Modbus server")

if __name__ == "__main__":
    writer = ModbusUnauthorizedCoilWriter()
    writer.run_test()
