import unittest
from unittest.mock import patch
import socket
from py_backend.health_checks.env_health_check import connnection_check, dns_check


class TestConnectionCheck(unittest.TestCase):
    @patch("socket.socket")
    def test_successful_connection(self, mock_socket):
        host = "example.com"
        port = 80

        # Mock the socket.connect method to simulate a successful connection
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.connect.return_value = None

        # Call the function with the provided host and port
        result = connnection_check(host, port)

        # Assert the function's behavior (expecting True for a successful connection)
        self.assertTrue(result)

        # Assert that the socket methods were called as expected
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_socket_instance.connect.assert_called_once_with((host, port))

    @patch("socket.socket")
    def test_failed_connection(self, mock_socket):
        host = "example.com"
        port = 80

        # Mock the socket.connect method to simulate a failed connection
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.connect.side_effect = socket.error("Connection refused")

        # Call the function with the provided host and port
        result = connnection_check(host, port)

        # Assert the function's behavior (expecting False for a failed connection)
        self.assertFalse(result)

        # Assert that the socket methods were called as expected
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_socket_instance.connect.assert_called_once_with((host, port))


if __name__ == "__main__":
    unittest.main()
