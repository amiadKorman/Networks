"""
Author: Amiad Korman
Date: 3/12/2022
"""
import socket
import select
import protocol

MAX_MSG_LENGTH = 1024
SERVER_IP = '0.0.0.0'


def set_name(client, name, clients):
    if name in clients.values():
        return f"The name {name} is already taken!"

    clients[client] = name
    return f"Hello {name}!"


def get_names(clients):
    return ', '.join(clients.values())


def exit_cmd(client, clients):
    if client in clients:
        clients.pop(client)
    return "Disconnected"


def send_msg(sender, receiver, msg, clients):
    if sender not in clients:
        return sender, "You must have a name to send a message!"

    if receiver not in clients.values():
        return sender, f"Client {receiver} does not exist"

    receiver_client = {i for i in clients if clients[i] == receiver}
    return receiver_client, msg


def create_server_rsp(client, data, clients):
    """
    Based on the command, create a proper response
    :param client: client socket that send the command
    :param data: the command from the client
    :param clients: dictionary of all the clients
    :return:
    """
    cmd = data.split()

    if cmd[0] == "NAME":
        if len(cmd) < 2:
            return client, "You must enter a name!"
        return client, set_name(client, cmd[1], clients)

    if cmd[0] == "GET_NAMES":
        if len(cmd) != 1:
            return client, "Too much parameters!"
        return client, get_names(clients)

    if cmd[0] == "MSG":
        if len(cmd) < 3:
            return client, "You must have at least 3 parameters!"
        return client, send_msg(client, cmd[1], ' '.join(cmd[2:]), clients)

    if cmd[0] == "EXIT":
        if len(cmd) != 1:
            return client, "Too much parameters!"
        return client, exit_cmd(client, clients)

    else:
        return client, "Unknown command!"


def print_client_sockets(client_sockets):
    for c in client_sockets:
        print("\t", c.getpeername())


def main():
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, protocol.PORT))
    server_socket.listen()
    print("Listening for clients...")

    client_sockets = []
    messages_to_send = []
    clients = {}

    while True:
        read_list = [server_socket] + client_sockets
        ready_to_read, ready_to_write, in_error = select.select(read_list, client_sockets, [])

        for current_socket in ready_to_read:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                # clients_dict = add_client_to_dict(client_socket, clients_dict)  # add new client to the dict.
                # print(clients_dict)
                client_sockets.append(connection)
                print_client_sockets(client_sockets)
            else:
                valid_data, data = protocol.get_msg(current_socket)
                if not valid_data:
                    # wrong protocol
                    data = "Wrong protocol"
                    print(data)
                    messages_to_send.append((current_socket, data))
                    current_socket.recv(MAX_MSG_LENGTH)  # clean possible garbage
                else:
                    if data == "EXIT":
                        # disconnect client from server
                        print("Connection closed")
                        client_sockets.remove(current_socket)
                        current_socket.close()
                        print_client_sockets(client_sockets)
                    else:
                        # create server response
                        message = create_server_rsp(current_socket, data, clients)
                        messages_to_send.append(message)

        for message in messages_to_send:
            # send response to clients
            current_socket, data = message
            if current_socket in ready_to_write:
                response = protocol.create_msg(data)
                current_socket.send(response.encode())
                messages_to_send.remove(message)


if __name__ == "__main__":
    main()
