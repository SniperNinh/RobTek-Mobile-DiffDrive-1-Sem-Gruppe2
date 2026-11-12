
import urllib.request
from linux_wii_remote import WiiRemote

wii_remote = WiiRemote()

PICO_IP = "10.170.221.80"

def send_message(message):

    url = f"http://10.170.221.80/"

    request = urllib.request.Request(
        url,
        data=message.encode(),
        method="POST",
        headers={"Content-Type": "text/plain"}
    )

    response = urllib.request.urlopen(request)

    print(response)
button_events = wii_remote.get_but_events()
while True:
    send_message("Button events: " + str(button_events))