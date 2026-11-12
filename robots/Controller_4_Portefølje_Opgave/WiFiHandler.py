import network
from time import sleep
import socket
# Wi-Fi credentials
ssid = 'NothingPhone(3)_9831'
password = 'h4pr7ee2shsacb4'

static_ip = '10.170.221.80'
subnet_mask = '255.255.255.0'
gateway_ip = '10.170.221.54'
dns_server = '1.1.1.1'

# Init Wi-Fi Interface
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Connect to your network
wlan.connect(ssid, password)

# Wait for Wi-Fi connection
connection_timeout = 0
print("blablæalba")
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



address = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(address)
server.listen(1)

print("Server started!")
print("Waiting for messages...")


while True:

    client, addr = server.accept()

    try:
        request = b""

        while b"\r\n\r\n" not in request:
            part = client.recv(512)

            if not part:
                break

            request += part

        if b"\r\n\r\n" in request:

            headers, body = request.split(b"\r\n\r\n", 1)

            content_length = 0

            for line in headers.split(b"\r\n"):
                if line.lower().startswith(b"content-length:"):
                    content_length = int(line.split(b":")[1].strip())

            while len(body) < content_length:
                part = client.recv(512)

                if not part:
                    break

                body += part

            message = body[:content_length].decode()

            print("Received message:", message)

        client.send(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Connection: close\r\n\r\n"
            b"Message received"
        )

    except Exception as e:
        print("Error:", e)

    finally:
        client.close()