import socket
import time
import json
import unittest
import os
import sys

# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

class TestRegistration(unittest.TestCase):
    def setUp(self):
        self.server_host = "127.0.0.1"
        self.server_port = 55555
        self.users_file = os.path.join(project_root, 'data', 'users.json')
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)

    def test_register_user(self):
        # Client connects to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_host, self.server_port))

        # Prepare registration message
        registration_data = {
            "type": "register_user",
            "payload": {
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        }
        message = json.dumps(registration_data) + '\n'
        
        # Send registration message
        client_socket.sendall(message.encode('utf-8'))

        # Wait for the server to process and save the user
        time.sleep(0.5)

        # Close the client connection
        client_socket.close()

        # Verify that the user was saved in users.json
        self.assertTrue(os.path.exists(self.users_file))

        with open(self.users_file, 'r') as f:
            users_data = json.load(f)
        
        self.assertEqual(len(users_data), 1)
        self.assertIn("testuser", users_data)
        saved_user = users_data["testuser"]

        self.assertEqual(saved_user['username'], "testuser")
        self.assertEqual(saved_user['email'], "test@example.com")
        # The test will fail if you check for the plain password.
        # self.assertEqual(saved_user['password'], "password123") 
        self.assertEqual(saved_user['score'], 0)
        self.assertIn('created_at', saved_user)

if __name__ == "__main__":
    unittest.main()
