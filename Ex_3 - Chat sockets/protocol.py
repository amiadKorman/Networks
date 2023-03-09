"""EX 3 protocol implementation
   Author: Amiad Korman
   Date: 3/12/2022
   Possible client commands:
    NAME <name> will set name. Server will reply error if duplicate
    GET_NAMES will get all names
    MSG <NAME> <message> will send message to client name
    EXIT will close client
"""

LENGTH_FIELD_SIZE = 2
PORT = 8820


def create_msg(data):
    """Create a valid protocol message, with length field"""
    msg = str(len(data)).zfill(LENGTH_FIELD_SIZE) + data
    return msg


def get_msg(my_socket):
    """Extract message from protocol, without the length field
       If length field does not include a number, returns False, "Error" """
    try:
        length = my_socket.recv(LENGTH_FIELD_SIZE).decode()
    except Exception as e:
        return False, e

    if length.isdigit():
        message = my_socket.recv(int(length)).decode()
        return True, message
    else:
        return False, "Error"
