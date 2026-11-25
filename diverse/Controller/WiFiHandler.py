import network
from time import sleep
import socket

class WifiHandler:
    def __init__(self, ssid, password, gateway_ip):
        # Wi-Fi credentials
        self.ssid = ssid
        self.password = password

        self.static_ip = '10.225.34.81'
        subnet_mask = '255.255.255.0'
        gateway_ip = gateway_ip
        dns_server = "1.1.1.1"

        # Init Wi-Fi Interface
        global wlan
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        # Connect to your network
        wlan.connect(ssid, password)

        # Wait for Wi-Fi connection
        connection_timeout = 0

        while connection_timeout < 20:
            if wlan.status() >= 3:
                break
            connection_timeout += 1
            print('Waiting for Wi-Fi connection...')
            sleep(1)

        # Check if connection is successful
        if wlan.status() != 3:
            connection_timeout = 0
            raise RuntimeError('Failed to establish a network connection')
            
        else:
            print('Connection successful!')
            network_info = wlan.ifconfig()
            print('IP address:', network_info[0])
            print('Subnet mask:', network_info[1])
            print('Gateway IP address:', network_info[2])
            print('DNS server IP address:', network_info[3])

            """network_info[0]: The IP address assigned to the Pico on the network.
            network_info[1]: The subnet mask.
            network_info[2]: The gateway IP address.
            network_info[3]: The DNS (Domain Name System) server IP address."""



        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(("0.0.0.0", 5000))

        print("Server started!")
        print("Waiting for messages...")


    def get_data(self):
        data, addr = self.server.recvfrom(32)

        y_axis = int.from_bytes(data[0:2], 'big') -500
        z_axis = int.from_bytes(data[2:4], 'big') -500
        held_buttons = data[4]
        return y_axis, z_axis, held_buttons
