from pymodbus.client import ModbusTcpClient
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class ModbusUnauthorizedReader:
    def __init__(self, host='localhost', port=502):
        self.host = host
        self.port = port

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

    def read_coils(self, start_addr=0, count=8):
        """Read coil status (binary outputs)"""
        try:
            result = self.client.read_coils(address=start_addr, count=count)
            if not result.isError():
                logger.info(f"Coil Status:")
                for i, value in enumerate(result.bits):
                    status = "ON" if value else "OFF"
                    logger.info(f"  Coil {start_addr + i}: {status}")
            return result.bits
        except Exception as e:
            logger.error(f"Failed to read coils: {e}")
            return None

    def read_discrete_inputs(self, start_addr=0, count=8):
        """Read discrete input status (binary inputs)"""
        try:
            result = self.client.read_discrete_inputs(address=start_addr, count=count)
            if not result.isError():
                logger.info(f"Discrete Input Status:")
                for i, value in enumerate(result.bits):
                    status = "ON" if value else "OFF"
                    logger.info(f"  Input {start_addr + i}: {status}")
            return result.bits
        except Exception as e:
            logger.error(f"Failed to read discrete inputs: {e}")
            return None

    def read_holding_registers(self, start_addr=0, count=4):
        """Read holding registers (analog outputs)"""
        try:
            result = self.client.read_holding_registers(address=start_addr, count=count)
            if not result.isError():
                logger.info(f"Holding Register Values:")
                for i, value in enumerate(result.registers):
                    logger.info(f"  Register {start_addr + i}: {value} (0x{value:04X})")
            return result.registers
        except Exception as e:
            logger.error(f"Failed to read holding registers: {e}")
            return None

    def read_input_registers(self, start_addr=0, count=4):
        """Read input registers (analog inputs)"""
        try:
            result = self.client.read_input_registers(address=start_addr, count=count)
            if not result.isError():
                logger.info(f"Input Register Values:")
                for i, value in enumerate(result.registers):
                    logger.info(f"  Register {start_addr + i}: {value} (0x{value:04X})")
            return result.registers
        except Exception as e:
            logger.error(f"Failed to read input registers: {e}")
            return None

    def run_comprehensive_scan(self):
        """Run a comprehensive scan of all register types"""
        if self.connect():
            logger.info("\nStarting comprehensive Modbus read operation...")
            self.read_coils()
            time.sleep(0.5)  # Prevent overwhelming the server
            self.read_discrete_inputs()
            time.sleep(0.5)
            self.read_holding_registers()
            time.sleep(0.5)
            self.read_input_registers()
            self.client.close()
        else:
            logger.error("Failed to connect to Modbus server")

if __name__ == "__main__":
    reader = ModbusUnauthorizedReader()
    reader.run_comprehensive_scan()
