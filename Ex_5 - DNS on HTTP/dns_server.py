# Ex 6 - DNS on HTTP
# Author: Amiad Korman
# Date: 08/02/2023

import random
import socket

from scapy.layers.inet import UDP, IP
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.sendrecv import sr1

SOCKET_IP = '0.0.0.0'
PORT = 8153
SOCKET_TIMEOUT = 5
MAX_GET_REQUEST_LENGTH = 2048
DNS_SERVER = "8.8.8.8"
D_PORT = 53

HTTP_VERSION = "HTTP/1.1"
HTTP_ERROR = f"{HTTP_VERSION} 500 Internal Server Error\r\n\r\n"
HTTP_OK = f"{HTTP_VERSION} 200 OK\r\n"
HTTP_NOT_FOUND = f"{HTTP_VERSION} 404 Not Found\r\n\r\n"

query_id = 0


def create_http_ok_response(data):
    """ create http ok 200 response """
    content_type = "Content-Type: text/html; charset=utf-8\r\n"
    content_length = 'Content-Length: ' + str(len(data)) + '\r\n\r\n'

    http_response = HTTP_OK + content_type + content_length
    return http_response.encode() + data


def get_port_rand():
    """ return random port number that isn't socket port """
    rand_port = random.randint(500, 2 ** 16)
    while rand_port == PORT:  # to not get the socket port
        rand_port = random.randint(500, 2 ** 16)

    return rand_port


def reverse_mapping(ip):
    """ return to client reverse mapping of requested ip"""
    global query_id
    query_id += 1

    address = '.'.join(ip.split('.')[::-1]) + '.in-addr.arpa'
    dns_request = IP(dst=DNS_SERVER) / UDP(sport=get_port_rand(),
                                           dport=D_PORT) / DNS(id=query_id, rd=1,
                                                               qd=DNSQR(qtype=12, qname=address))
    try:
        dns_response = sr1(dns_request, timeout=3, verbose=0)
        if dns_response and dns_response.haslayer(DNS) and dns_response[DNS].ancount > 0:
            return dns_response[DNS].an[0].rdata.decode()
        else:
            return 'Wrong-Name-error'
    except Exception as e:
        print('Exception', e)
        return 'No connection to the internet!'


def get_ips_scapy(address):
    """ return to client all the addresses of the requested site"""
    global query_id
    query_id += 1

    dns_request = IP(dst=DNS_SERVER) / UDP(sport=get_port_rand(),
                                           dport=D_PORT) / DNS(id=query_id,
                                                               qd=DNSQR(qtype=1, qname=address))
    try:
        dns_response = sr1(dns_request, timeout=3, verbose=0)
        if dns_response[DNS].rcode == 0:
            return '<br />'.join([dns_response[DNSRR][i].rdata for i in range(1, dns_response[DNS].ancount)])
        else:
            return f"Can't find ip addresses for {address}"
    except Exception as e:
        print('Exception', e)
        return 'No connection to the internet!'


def handle_client_request(resource, client_socket, is_ptr):
    """ Check the required resource, generate proper HTTP response and send to client """
    if is_ptr:
        data = reverse_mapping(resource)
    else:
        data = get_ips_scapy(resource)

    client_socket.send(create_http_ok_response(data.encode()))


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

            if method == "GET" and version == HTTP_VERSION:
                print(url)
                return True, url

    return False, ""


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP,
    calls function to handle the requests """
    print('Client connected')

    while True:
        client_request = client_socket.recv(MAX_GET_REQUEST_LENGTH).decode()

        valid_http, resource = validate_http_request(client_request)

        if valid_http:
            print('Got a valid HTTP request')
            if resource.startswith(r'reverse/'):
                print('Type PTR')
                handle_client_request(resource.strip('reverse/'), client_socket, True)
            else:
                print('Type A')
                handle_client_request(resource, client_socket, False)
            break
        else:
            print('Error: Not a valid HTTP request')
            client_socket.send(HTTP_ERROR.encode())
            break

    print('Closing connection')
    print('--------------------------------------------------')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SOCKET_IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        try:
            handle_client(client_socket)
        except socket.timeout:
            print("timeout")


if __name__ == "__main__":
    # Call the main handler function
    main()
