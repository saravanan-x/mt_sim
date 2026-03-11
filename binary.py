import socket

HOST = "0.0.0.0"   # listen on all interfaces
PORT = 5000

def extract_message(img_bytes):

    offset = 500
    bits = []

    # extract LSB bits from image
    for b in img_bytes[offset:]:
        bits.append(b & 1)

    # get message length (first 16 bits)
    msg_len = 0
    for i in range(16):
        msg_len = (msg_len << 1) | bits[i]

    index = 16
    message_bytes = []

    for _ in range(msg_len):

        byte = 0

        for _ in range(8):

            if index >= len(bits):
                return "Message extraction failed"

            byte = (byte << 1) | bits[index]
            index += 1

        message_bytes.append(byte)

    try:
        return bytes(message_bytes).decode()
    except:
        return "Decode error"


server = socket.socket()
server.bind((HOST, PORT))
server.listen(5)

print("Server listening...")

count = 0

while True:

    conn, addr = server.accept()
    print("Connected:", addr)

    data = b''

    while True:
        packet = conn.recv(4096)
        if not packet:
            break
        data += packet

    conn.close()

    # convert HEX → image
    hex_string = data.decode()
    img_bytes = bytes.fromhex(hex_string)

    filename = f"esp32_image_{count}.jpg"

    with open(filename, "wb") as f:
        f.write(img_bytes)

    print("Saved:", filename)

    # print(hex_string)

    # extract hidden message
    message = extract_message(img_bytes)
    print("Hidden message:", message)

    count += 1