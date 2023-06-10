
import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from ..models.user import User
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token


def user():
    # Create a user and add them to the database
        user = User(id=1, email="student@test.com",username="testUser", password_hash="password")
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=user.email)
        headers={
            "Authorization": f"Bearer {token}"
        }
        return headers



class UserTestCase(unittest.TestCase):
    
    def setUp(self):

        self.app = create_app(config=config_dict['test'])

        self.appctx = self.app.app_context()

        self.appctx.push()

        self.client = self.app.test_client()

        db.create_all()


    def tearDown(self):

        db.drop_all()

        self.appctx.pop()

        self.app = None

        self.client = None


    def test_user_registration(self):

        data = {
            "username": "Test User",
            "email": "testuser@gmail.com",
            "password": "password"
        }

        response = self.client.post('/auth/signup', json=data)

        user = User.query.filter_by(email='testuser@gmail.com').first()

        assert user.username == "Test User"

        assert response.status_code == 201

    def test_user_login(self):
        data = {
            "email":"testuser@gmail.com",
            "password": "password"
        }
        response = self.client.post('/auth/login', json=data)

        assert response.status_code == 200
# test for changing password 
    def test_reset_password(self):
            headers= user()

            data = {
                 "old_password":"password",
                 "new_password":"new_password"
            }

            response = self.client.patch("/auth/reset_password",json=data, headers=headers)
            assert response.status_code == 200