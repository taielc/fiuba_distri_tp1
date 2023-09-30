from socket import socket, AF_INET, SOCK_STREAM


def create_socket():
    return socket(AF_INET, SOCK_STREAM)
