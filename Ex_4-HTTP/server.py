# Ex 5 - HTTP Server Shell
# Author: Amiad Korman

import os
import socket

IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 0.1
MAX_GET_REQUEST_LENGTH = 2048
LOCAL_HOST = "http://127.0.0.1"
ROOT_DIRECTORY = r"C:\Networks\work\webroot"
HTTP_OK = "HTTP/1.0 200 OK\r\n"
HTTP_NOT_FOUND = "HTTP/1.0 404 Not Found\r\n\r\n"
HTTP_REDIRECTION = "HTTP/1.0 302 Found\r\n"
REDIRECTION_DICTIONARY = {"cat": "imgs/abstract.jpg"}


def get_file_data(filename):
    """ Get data from file """
    # Open the file in binary mode
    with open(filename, 'rb') as f:
        # Read the file content
        data = f.read()
    return data


def calculate_area(url):
    """Try to calculate area of triangle with given parameters in URL"""
    components = url.split('?')
    try:
        params = components[1].split('&')
        height = params[0].split('=')[1]
        width = params[1].split('=')[1]
        height = float(height)
        width = float(width)
        if height <= 0 or width <= 0:
            raise Exception("Must be more then 0")
    except Exception as e:
        return "Error: {}".format(e)

    area = height * width / 2
    return area


def set_content_type(url):
    """Extract requested file type from URL (txt, html, jpg, js, css)"""
    if url.endswith(".txt") or url.endswith(".html"):
        return 'text/html; charset=utf-8\r\n'
    elif url.endswith(".jpg"):
        return 'image/jpeg\r\n'
    elif url.endswith(".js"):
        return 'text/javascript; charset=UTF-8\r\n'
    elif url.endswith(".css"):
        return 'text/css\r\n'
    elif url.endswith(".ico"):
        return 'image/x-icon\r\n'
    elif url.endswith(".gif"):
        return 'image/gif\r\n'
    else:
        return '\r\n'


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    print(resource)
    if resource == '':
        url = "index.html"
    elif resource.startswith("calculate-area?"):
        area = calculate_area(resource)
        http_header = HTTP_OK
        content_type = "Content-Type: text/plain\r\n"
        data = str(area).encode()
        content_length = 'Content-Length: ' + str(len(data)) + '\r\n\r\n'
        http_response = http_header + content_type + content_length
        http_response = http_response.encode() + data
        client_socket.send(http_response)
        return
    else:
        url = resource.replace('/', '\\')

    # TO DO: check if URL had been redirected, not available or other error code. For example:
    if url in REDIRECTION_DICTIONARY:
        # TO DO: send 302 redirection response
        http_header = HTTP_REDIRECTION
        location = f"Location: {LOCAL_HOST}:{PORT}/{REDIRECTION_DICTIONARY.get(url)}\r\n\r\n"
        response = http_header + location
        client_socket.send(response.encode())
        return

    filename = os.path.join(ROOT_DIRECTORY, url)
    if os.path.isfile(filename):
        # extract requested file type from URL (txt, html, jpg, js, css)
        http_header = HTTP_OK
        content_type = "Content-Type: " + set_content_type(url)

        data = get_file_data(filename)
        content_length = 'Content-Length: ' + str(len(data)) + '\r\n'
        http_response = http_header + content_type + content_length + '\r\n'
        http_response = http_response.encode()
        http_response += data
        client_socket.send(http_response)
    else:
        # Construct and send the response
        response = HTTP_NOT_FOUND
        client_socket.send(response.encode())


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
    """
    # Split the request into individual lines
    lines = request.split("\r\n")
    # Check if the request is at least 3 lines long
    if not len(lines) < 3:
        # Get the first line of the request, which contains the request method, URL, and HTTP version
        first_line = lines[0]
        # Split the first line into separate components
        first_line_components = first_line.split(" ")
        # Check if the first line has at least 3 components (method, URL, and HTTP version)
        if len(first_line_components) == 3:
            # Get the request method (GET, POST, etc.)
            method = first_line_components[0]
            url = first_line_components[1][1:]
            version = first_line_components[2]

            if method == "GET" and version == "HTTP/1.1":
                print(url)
                return True, url

    return False, ""


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')

    while True:
        # TO DO: insert code that receives client request
        try:
            client_request = client_socket.recv(MAX_GET_REQUEST_LENGTH).decode()
        except Exception as e:
            print(e)
            break
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
            break
        else:
            print('Error: Not a valid HTTP request')
            break

    print('Closing connection')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)


if __name__ == "__main__":
    # Call the main handler function
    main()
