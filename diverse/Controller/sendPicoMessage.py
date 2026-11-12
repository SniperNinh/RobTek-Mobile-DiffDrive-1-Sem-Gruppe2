import socket
from linux_wii_remote import WiiRemote
import random, time

#wii_remote = WiiRemote()

PICO_IP = "10.238.177.71"


# Create UDP socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_command(command):
    data = command.to_bytes(2, byteorder='little')
    client.sendto(data, (PICO_IP, 5000))


# Test commands
while True:
    random_value = random.randint(0, 500)
    print(random_value)
    send_command(random_value)
    time.sleep(0.02)
