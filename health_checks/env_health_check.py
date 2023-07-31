"""Environment Health Check

This script checks the connection to the key services.  It also
provides error messages if there are any issues.

This file should check these domains:
    * up-osprey-6230-us1-kafka.upstash.io

This file should check for connectivity on this list of connections:
    * up-osprey-6230-us1-kafka.upstash.io:9092
    * 8.8.8.8:53

This file can also be imported as a module and contains the following
functions:
    * connnection_check - checks the connection to the key services
    * dns_check - checks the dns resolution for the specified domain name
    * handle_health_checks - calls all the health check functions
"""

import socket


def connnection_check(host, port, timeout=3):
    """Checks the connection to the key services.

    Args:
      host: The host name to check.
      port: The port number to check.
      timeout: The timeout value to use.

    Returns:
      Should print status of either success or failure.
      True if the connection was successful, otherwise False.
    """
    print(f"Trying to connect to: {host}:{port}")
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        # print conntect with host and port successfully
        print(f"Connected to: {host}:{port}")
        return True
    except socket.error as ex:
        # print error with host and port
        print(f"Connection to: {host}:{port} failed.")
        print(ex)
        return False


def dns_check(domain_name):
    """Checks the dns resolution for the specified domain name.

    Args:
      domain_name: The domain name to resolve.

    Returns:
      Should print status of either success or failure.
      True if the domain name was resolved, otherwise False.
    """

    try:
        socket.gethostbyname(domain_name)
        print(f"DNS resolution for {domain_name} was successful.")
        return True
    except socket.error as ex:
        print(f"DNS resolution for {domain_name} failed.")
        print(ex)
        return False


def handle_health_checks():
    """Calls all the health check functions."""
    connnection_check(host="up-osprey-6230-us1-kafka.upstash.io", port=9092)
    connnection_check(host="8.8.8.8", port=53)
    dns_check(domain_name="up-osprey-6230-us1-kafka.upstash.io")


if __name__ == "__main__":
    handle_health_checks()
