# -*- coding: utf-8 -*-

import socket
import sys
import datetime
import json
import time
import argparse

try:
    import serial
except ImportError:
    serial = None


class WeightReceiver:
    def __init__(self, connection_type='ethernet', host='127.0.0.1', port=8080,
                 com_port=None, baudrate=9600, output_file='weights.json'):
        self.connection_type = connection_type
        self.host = host
        self.port = port
        self.com_port = com_port
        self.baudrate = baudrate
        self.output_file = output_file
        self.socket = None
        self.serial_port = None
        self.connected = False

    def connect(self):
        try:
            if self.connection_type == 'ethernet':
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                self.connected = True
                print(f"Connected to {self.host}:{self.port} via Ethernet")

            elif self.connection_type == 'com':
                if serial is None:
                    print("Error: pyserial is not installed. Install it with: pip install pyserial")
                    sys.exit(1)
                self.serial_port = serial.Serial(
                    port=self.com_port,
                    baudrate=self.baudrate,
                    timeout=1
                )
                self.connected = True
                print(f"Connected to {self.com_port} at {self.baudrate} baud via COM port")
            else:
                print(f"Unsupported connection type: {self.connection_type}")
                sys.exit(1)
        except Exception as e:
            print(f"Connection error: {e}")
            sys.exit(1)

    def send_command(self, command):
        try:
            if self.connection_type == 'ethernet':
                self.socket.sendall(command.encode())
            elif self.connection_type == 'com' and self.serial_port:
                self.serial_port.write(command.encode())
        except Exception as e:
            print(f"Error sending the command: {e}")

    def receive_response(self):
        try:
            if self.connection_type == 'ethernet':
                response = self.socket.recv(1024).decode().strip()
            elif self.connection_type == 'com' and self.serial_port:
                response = self.serial_port.readline().decode().strip()
            else:
                response = ""
            return response
        except Exception as e:
            print(f"Error receiving the response: {e}")
            return ""

    def read_weight(self):
        try:
            self.send_command("READ\n")  # Команда может отличаться для вашего оборудования
            response = self.receive_response()
            if response:
                # Парсинг ответа — адаптируйте под формат вашего оборудования
                weight_str = response.split()[0]  # Берём первое слово как вес
                return float(weight_str)
            return None
        except Exception as e:
            print(f"Weight reading error: {e}")
            return None

    def save_to_file(self, weight):
        try:
            with open(self.output_file, 'a') as f:
                data = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "weight": weight,
                    "source": f"{self.connection_type.upper()}:{self.host if self.connection_type=='ethernet' else self.com_port}"
                }
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            print(f"Error writing to a file: {e}")

    def disconnect(self):
        try:
            if self.connection_type == 'ethernet' and self.socket:
                self.socket.close()
            elif self.connection_type == 'com' and self.serial_port:
                self.serial_port.close()
            print("The connection is closed")
        except Exception as e:
            print(f"Error closing the connection: {e}")

    def run(self, interval=5):
        try:
            self.connect()
            print("The program is running. To exit, press Ctrl+C")
            while True:
                weight = self.read_weight()
                if weight is not None:
                    print(f"Weight gained: {weight} kg")
                    self.save_to_file(weight)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nThe program was stopped by the user")
        finally:
            self.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weight data acquisition program with TerminalName")
    parser.add_argument('--type', choices=['ethernet', 'com'], default='ethernet',
                        help='Connection type: ethernet or com')
    parser.add_argument('--host', default='127.0.0.1', help='The terminals IP address (for ethernet)')
    parser.add_argument('--port', type=int, default=8080, help='Connection port (for ethernet)')
    parser.add_argument('--com-port', default=None, help='COM port name (for com, e.g., COM3 or /dev/ttyUSB0)')
    parser.add_argument('--baudrate', type=int, default=9600, help='Baud rate for COM port')
    parser.add_argument('--file', default='weights.json', help='A file for saving data')
    parser.add_argument('--interval', type=int, default=5, help='Polling interval in seconds')

    args = parser.parse_args()

    receiver = WeightReceiver(
        connection_type=args.type,
        host=args.host,
        port=args.port,
        com_port=args.com_port,
        baudrate=args.baudrate,
        output_file=args.file
    )
    receiver.run(interval=args.interval)
