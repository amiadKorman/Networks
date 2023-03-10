"""EX 2.6 server implementation
   Author: Amiad Korman
   Date: 9/11/2022
   Update date: 21/11/2022
   Possible client commands defined in protocol.py
"""
import datetime
import random
import socket
import protocol


def create_server_rsp(cmd):
    """Based on the command, create a proper response"""
    if cmd == "NUMBER":
        return str(random.randint(0, 99))
    if cmd == "HELLO":
        return "Meravnik"
    if cmd == "TIME":
        return f"The time is: {datetime.datetime.now()}"
    if cmd == "EXIT":
        return "Bye"
    else:
        return "Error"


def check_cmd(data):
    """Check if the command is defined in the protocol (e.g NUMBER, HELLO, TIME, EXIT)"""
    if data in ['NUMBER', 'HELLO', 'TIME', 'EXIT']:
        return True
    else:
        return False


def create_error_msg():
    """Create error message to return to the client"""
    return "Wrong protocol"


def main():
    # Create TCP/IP socket object
    server_socket = socket.socket()
    # Bind server socket to IP and Port
    server_socket.bind(("0.0.0.0", protocol.PORT))
    # Listen to incoming connections
    server_socket.listen()
    print("Server is up and running")
    # Create client socket for incoming connection
    (client_socket, client_address) = server_socket.accept()
    print("Client connected")

    while True:
        # Get message from socket and check if it is according to protocol
        valid_msg, cmd = protocol.get_msg(client_socket)
        if valid_msg:
            # 1. Print received message
            print(f"Client sent: {cmd}")
            # 2. Check if the command is valid, use "check_cmd" function
            # 3. If valid command - create response
            if check_cmd(cmd):
                reply = create_server_rsp(cmd)
            else:
                reply = create_error_msg()
        else:
            reply = create_error_msg()
            client_socket.recv(1024)  # Attempt to empty the socket from possible garbage

        msg = protocol.create_msg(reply).encode()
        # Send response to the client
        client_socket.send(msg)
        # If EXIT command, break from loop
        if cmd == "EXIT":
            break

    print("Closing\n")
    # Close sockets
    client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    main()
