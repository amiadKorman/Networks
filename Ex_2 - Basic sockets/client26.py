"""EX 2.6 client implementation
   Author: Amiad Korman
   Date: 9/11/2022
   Update date: 21/11/2022
   Possible client commands defined in protocol.py
"""

import socket
import protocol

COMMANDS = ['NUMBER', 'HELLO', 'TIME', 'EXIT']


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect(("127.0.0.1", protocol.PORT))

    while True:
        user_input = input(f"Enter command: {COMMANDS}\n")
        if 99 < len(user_input) or len(user_input) == 0:
            print("Wrong protocol")
            continue
        # 1. Add length field ("HELLO" -> "04HELLO")
        user_msg = protocol.create_msg(user_input)
        # 2. Send it to the server
        my_socket.send(user_msg.encode())
        # 3. Get server's response
        valid_msg, data = protocol.get_msg(my_socket)
        # 4. If server's response is valid, print it
        if valid_msg:
            print(f"Server sent: {data}\n")
        else:
            print("Wrong protocol")
            my_socket.recv(1024)  # Attempt to empty the socket from possible garbage

        # 5. If command is EXIT(server sent "bye"), break from while loop
        if data == "Bye":
            break

    print("Closing\n")
    # Close socket
    my_socket.close()


if __name__ == "__main__":
    main()
