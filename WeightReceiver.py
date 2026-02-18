# -*- coding: utf-8 -*-

import socket
import sys
import datetime
import json

class WeightReceiver:
    def __init__(self, host='127.0.0.1', port=8080, output_file='weights.json'):
        self.host = host
        self.port = port
        self.output_file = output_file
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to {self.host}:{self.port}")
        except Exception as e:
            print(f"Connection error: {e}")
            sys.exit(1)

    def send_command(self, command):
        try:
            self.socket.sendall(command.encode())
        except Exception as e:
            print(f"Error sending the command: {e}")

    def receive_response(self):
        try:
            response = self.socket.recv(1024).decode().strip()
            return response
        except Exception as e:
            print(f"Error receiving the response: {e}")
            return ""

    def read_weight(self):
        try:
            self.send_command("READ\n")  # Пример команды, может отличаться
            response = self.receive_response()
            if response:
                weight = response.split()[0]  # Пример парсинга
                return float(weight)
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
                    "source": "TerminalName"
                }
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            print(f"Error writing to a file: {e}")

    def disconnect(self):
        try:
            self.socket.close()
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
    import time
    import argparse

    parser = argparse.ArgumentParser(description="Weight data acquisition program with TerminalName")
    parser.add_argument('--host', default='127.0.0.1', help='The terminals IP address')
    parser.add_argument('--port', type=int, default=8080, help='Connection port')
    parser.add_argument('--file', default='weights.json', help='A file for saving data')
    parser.add_argument('--interval', type=int, default=5, help='Polling interval in seconds')

    args = parser.parse_args()

    receiver = WeightReceiver(
        host=args.host,
        port=args.port,
        output_file=args.file
    )
    receiver.run(interval=args.interval)
