import os
import unittest
from flask import current_app
from app import create_app, db
from app.models import User

class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # Use in-memory database
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_home_page_redirect(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_user_registration(self):
        # Test user registration
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'test_password',
            'confirm_password': 'test_password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')

    def test_user_login(self):
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('test_password')
        db.session.add(user)
        db.session.commit()

        # Test login with correct credentials
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'test_password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Test login with incorrect credentials
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'wrong_password'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)

    def test_logout(self):
        # Create and login a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('test_password')
        db.session.add(user)
        db.session.commit()

        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'test_password'
        })

        # Test logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
