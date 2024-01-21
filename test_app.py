import unittest
from flask import url_for
from app import app, db, User, Movie, EmailConfirmationToken  # Import your Flask application and models here

# app_context: application's environment, needed interact with the application setup or configuration, but no request is in progress
# test_request_context: 

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app # a reference to your Flask application instance
        self.client = self.app.test_client() # use to make requests to your application in your tests
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False # disable CSRF protection in testing environments
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        # self.context = self.app.app_context()
        self.context = self.app.test_request_context()
        self.context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_index(self):
        # with self.app.test_request_context():
        response = self.client.get(url_for('index'))
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        # with self.app.test_request_context():
        user = User(username='test', email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()

        # uses the test client to make a POST request to the login route, passing in the username and password as form data
        response = self.client.post(url_for('login'), data=dict(
            identifier='test',
            password='testpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login success.', response.data)

    # Add more tests as needed

if __name__ == '__main__':
    unittest.main()
