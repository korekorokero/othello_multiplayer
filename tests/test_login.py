import socket
import json
import unittest
import os
import sys
import time
import uuid

# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from server.protocols import Protocol

class TestLogin(unittest.TestCase):
    def setUp(self):
        self.server_host = "127.0.0.1"
        self.server_port = 55555
        self.users_file = os.path.join(project_root, 'data', 'users.json')
        self.test_user_id = str(uuid.uuid4())
        self.test_user = {
            "user_id": self.test_user_id,
            "username": "testloginuser",
            "email": "login@example.com",
            "password": "password123",
            "score": 0
        }

        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)

        # Create a dummy user file for testing
        with open(self.users_file, 'w') as f:
            json.dump({self.test_user_id: self.test_user}, f, indent=4)

    def _send_and_receive(self, message):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_host, self.server_port))
        client_socket.sendall(message.encode('utf-8'))
        response_str = client_socket.recv(1024).decode('utf-8')
        client_socket.close()
        return Protocol.parse_message(response_str)

    def test_login_success(self):
        login_data = {
            "type": "login_user",
            "payload": {
                "username": "testloginuser",
                "password": "password123"
            }
        }
        message = json.dumps(login_data) + '\n'
        
        response = self._send_and_receive(message)

        self.assertIsNotNone(response)
        self.assertEqual(response['type'], 'user_logged_in')
        self.assertTrue(response['payload']['success'])
        self.assertEqual(response['payload']['user']['username'], 'testloginuser')

    def test_login_fail_wrong_password(self):
        login_data = {
            "type": "login_user",
            "payload": {
                "username": "testloginuser",
                "password": "wrongpassword"
            }
        }
        message = json.dumps(login_data) + '\n'

        response = self._send_and_receive(message)

        self.assertIsNotNone(response)
        self.assertEqual(response['type'], 'user_logged_in')
        self.assertFalse(response['payload']['success'])

if __name__ == "__main__":
    unittest.main()
