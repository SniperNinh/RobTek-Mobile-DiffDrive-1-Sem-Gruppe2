import socket
from linux_wii_remote import WiiRemote
import random, time, evdev

wii_remote = WiiRemote()

PICO_IP = "10.230.172.71"


# Create UDP socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_wii_info(y_value, z_value, buttons_int):
    data = bytes(5)
    y_bytes = y_value.to_bytes(2, 'big')
    z_bytes = z_value.to_bytes(2, 'big')
    held_button_byte = buttons_int.to_bytes(1, 'big')
    data = y_bytes + z_bytes + held_button_byte
    y_axis = int.from_bytes(data[0:2], 'big') -600
    z_axis = int.from_bytes(data[2:4], 'big') -600
    held_buttons = data[4]
    print(y_axis, z_axis, held_buttons)
    client.sendto(data, (PICO_IP, 5000))


# Test commands
while True:
    acc_val = wii_remote.get_acc_val()
    held_buttons = wii_remote.buttons.active_keys()
    held_button_int = 0
    held_button_int |= (304 in held_buttons) << 1
    held_button_int |= (305 in held_buttons)

    # now we contruct a byte with the composition
    send_wii_info(acc_val[1]+620, acc_val[2]+600, held_button_int)
    time.sleep(0.1)