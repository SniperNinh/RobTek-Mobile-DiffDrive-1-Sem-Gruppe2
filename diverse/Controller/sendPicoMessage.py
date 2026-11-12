import socket
from linux_wii_remote import WiiRemote

wii_remote = WiiRemote()

PICO_IP = "10.170.221.80"


# Create UDP socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_command(command):
    data = command.to_bytes(2, byteorder='big', signed=True)
    client.sendto(data, (PICO_IP, 5000))


# Test commands
send_command(1)
send_command(2)
send_command(0)