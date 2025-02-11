import unittest
from flask import json
from config import app, init_db

# filepath: /home/user/Server/test_config.py

class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            init_db()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>WebSocket Client</title>', response.data)

    def test_device_uuid(self):
        response = self.app.get('/uuid')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('uuid', data)

    def test_login_success(self):
        response = self.app.post('/login', json={
            'username': 'admin',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)

    def test_login_failure(self):
        response = self.app.post('/login', json={
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_status_logged_in(self):
        # First, log in the user
        response = self.app.post('/login', json={
            'username': 'admin',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)

        response = self.app.get('/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['logged_in'])

    def test_status_logged_out(self):
        response = self.app.get('/status')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['logged_in'])

    def test_logout(self):
        # First, log in the user
        response = self.app.post('/login', json={
            'username': 'admin',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)

        response = self.app.post('/logout')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

if __name__ == '__main__':
    unittest.main()
