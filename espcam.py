import network
import socket
import camera
import time
import urandom
import machine

SSID = "bps_wifi"
PASSWORD = "sagabps@235"

SERVER_IP = "192.168.1.7"
PORT = 5000

words = ["rock","arch","black hat","tree","water","fish"]

# convert integer → bits
def int_to_bits(value, bits):
    out = []
    for i in range(bits):
        out.append((value >> (bits-1-i)) & 1)
    return out


def embed_message(img_bytes, message):

    msg_bytes = message.encode()
    msg_len = len(msg_bytes)

    data = bytearray(img_bytes)

    bits = []

    bits += int_to_bits(msg_len,16)

    offset = 500

    for b in img_bytes[offset:]:
        bits.append(b & 1)

    offset = 500   # skip JPEG header

    for i in range(len(bits)):
    if offset + i < len(data):
        data[offset + i] = (data[offset + i] & 0xFE) | bits[i]

    return bytes(data)


# WIFI CONNECT
wifi = network.WLAN(network.STA_IF)
wifi.active(False)
time.sleep(1)

wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting WiFi...")

timeout = 15
while not wifi.isconnected():

    time.sleep(1)
    timeout -= 1

    if timeout == 0:
        print("WiFi failed, rebooting")
        machine.reset()

print("Connected:", wifi.ifconfig())


# CAMERA INIT
camera.init(0, format=camera.JPEG, framesize=camera.FRAME_QQVGA)

print("Camera ready")

while True:

    print("Capturing image...")

    buf = camera.capture()

    print("Image size:", len(buf))

    # choose random words
    w1 = words[urandom.getrandbits(3) % len(words)]
    w2 = words[urandom.getrandbits(3) % len(words)]

    message = w1 + "," + w2

    print("Hidden message:", message)

    new_img = embed_message(buf, message)

    # convert image to HEX
    hex_data = ""

    for b in new_img:
        hex_data += "%02x" % b

    try:

        print("Connecting to server...")

        s = socket.socket()
        s.connect((SERVER_IP, PORT))

        print("Sending image...")

        chunk = 1024

        for i in range(0, len(hex_data), chunk):
            s.send(hex_data[i:i+chunk])

        s.close()

        print("Image sent")

    except Exception as e:
        print("Send failed:", e)

    print("Waiting 60 seconds...\n")

    time.sleep(30)