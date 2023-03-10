"""
Author: Amiad Korman
Date: 3/12/2022
"""
import select
import socket
import protocol
import msvcrt

COMMANDS = ['NAME <name>', 'GET_NAMES', 'MSG <name> <message>', 'EXIT']
CLIENT_IP = "127.0.0.1"


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((CLIENT_IP, protocol.PORT))
    print(f"Please enter commands: {COMMANDS}\n")

    msg = ''

    while True:
        if msvcrt.kbhit():
            char = msvcrt.getch()
            char = str(char.decode())
            print(char, flush=True, end='')
            if char == '\r' or char == '\n':
                msg = protocol.create_msg(msg)
                my_socket.send(msg.encode())
                if msg[protocol.LENGTH_FIELD_SIZE:] == "EXIT":
                    print("Disconnecting from the server...")
                    my_socket.close()
                    return
                msg = ''
            else:
                msg += char

        ready_to_read, ready_to_write, in_error = select.select([my_socket], [], [], 0)
        if ready_to_read:
            valid_msg, msg = protocol.get_msg(my_socket)
            if valid_msg:
                print("\nServer sent:", msg)
            else:
                print("Bad message")
        read_list = [my_socket]
        write_list = [my_socket]
        ready_to_read, ready_to_write, in_error = select.select(read_list, write_list, [])

        for current_socket in ready_to_read:
            valid_msg, msg = protocol.get_msg(current_socket)
            if valid_msg:
                print("Server sent:", msg)
            else:
                print("Bad message")

        for current_socket in ready_to_write:
            data = ''
            while msvcrt.kbhit():
                char = msvcrt.getch()
                char = str(char.decode())

                print(char, flush=True, end='')
                if char == '\r':
                    current_socket.send(protocol.create_msg(data).encode())
                    if data == "EXIT":
                        print("Disconnecting")
                        my_socket.close()
                        return
                    data = ''
                else:
                    data += char

    my_socket.close()


if __name__ == "__main__":
    main()
