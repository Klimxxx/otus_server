import socket
import random
from http import HTTPStatus

HOST = "127.0.0.1"
PORT = random.randint(10000, 20000)

with socket.socket() as serv_socket:
    print(f"Binding to {HOST}:{PORT}")
    serv_socket.bind((HOST, PORT))
    serv_socket.listen()
    print("Server is listening...")

    while True:
        print("Waiting for a connection...")
        connection, address = serv_socket.accept()
        print("Connection from", address)

        data = connection.recv(1024).decode().strip()
        print(f"Received data:\n{data}\n")

        # дефолтный статус ответа
        status_value = 200
        status_phrase = "OK"

        try:
            # парсим статус из реквестс
            request_line = data.split("\r\n")[0]
            request_method, request_uri, http_version = request_line.split()

            if "status=" in request_uri:
                status_code = int(request_uri.split("status=")[1].split("&")[0])
                status = HTTPStatus(status_code)
                status_value = status_code
                status_phrase = status.phrase
        except (ValueError, IndexError, KeyError) as e:
            print(f"Error parsing status: {e}")

        status_line = f"{http_version} {status_value} {status_phrase}"
        response_headers = "\r\n".join(data.split("\r\n")[1:])

        response = (
            f"{status_line}\r\n\r\n"
            f"Request Method: {request_method}\r\n"
            f"Request Source: {address}\r\n"
            f"Response Status: {status_value} {status_phrase}\r\n\r\n"
            f"{response_headers}"
        )

        connection.sendall(response.encode())
        connection.close()
