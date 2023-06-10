import unittest
from unittest.mock import patch
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from werkzeug.security import generate_password_hash
from ..models.user import User
from ..models.url import Url
from flask_jwt_extended import create_access_token
from http import HTTPStatus


def user():
    # Create a user and add them to the database
        user = User( email="student@test.com",username="testUser", password_hash="password")
        user.save()
        token = create_access_token(identity=user.email)
        headers={
            "Authorization": f"Bearer {token}"
        }
        return headers

class UrlTestCase(unittest.TestCase):

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

# test for shortening url
    def test_to_shorten_url(self):
        data = {
                'main_url': 'https://www.google.com/search?q=test&oq=test&aqs=chrome..69i57j0i271l2j69i60l3.1824j0j7&sourceid=chrome&ie=UTF-8',
                'title': 'Example Title'
        }
        
        headers= user()
        response = self.client.post("/url/short_url",json=data, headers=headers)

        assert response.status_code == 201
        assert 'url_code' in response.json
        assert 'title' in response.json
        assert 'long_url' in response.json
        assert 'short_url' in response.json
        

# test for customizing url 
    def test_to_customize_url(self):
        data = {
                'custom_domain': 'example.com',
                'url_path': 'custom-url-path'
            }
        
        headers= user()
        response = self.client.post("/url/customize_url", json=data, headers=headers)

        assert response.status_code == 201

# test for getting all urls
    def test_get_all_urls(self):
   
        response = self.client.get("/url/urls")
        assert response.status_code == 200
        assert response.json == []
        


# test for getting all urls by user id
    def test_get_all_urls(self):

        # Create a test user and generate JWT access token
        user = User( email='test@example.com',username="testUser", password_hash="password")
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(identity=user.email)  

        # Create a test URL associated with the test user
        url = Url(long_url='https://example.com', 
                  short_url='https://darrkzero.pythonanywhere.com/abc123',
                  url_code="abc123",
                  user_id=user.id, 
                  title='Example Title')
        url.save()

        response = self.client.get(f"/url/urls/{user.id}",  headers={"Authorization": f"Bearer {access_token}"})
        
        assert response.status_code == HTTPStatus.OK
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        assert response.json[0]['long_url'] == 'https://example.com'
        assert response.json[0]['short_url'] == 'https://darrkzero.pythonanywhere.com/abc123'
   
   
#    test for deleting a single url by url id 
    def test_delete_single_url(self):
         # Create a test user and generate JWT access token
        user = User( email='test@example.com',username="testUser", password_hash="password")
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(identity=user.email)  

        # Create a test URL associated with the test user
        url = Url(long_url='https://example.com', 
                  short_url='https://darrkzero.pythonanywhere.com/abc123',
                  url_code="abc123",
                  user_id=user.id, 
                  title='Example Title')
        url.save()
        response = self.client.delete(f"/url/{url.id}", headers={"Authorization": f"Bearer {access_token}"})

        assert response.status_code == HTTPStatus.OK

    #  test for geting a single url by url id 
    def test_get_single_url(self):
         # Create a test user and generate JWT access token
        user = User( email='test@example.com',username="testUser", password_hash="password")
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(identity=user.email)  

        # Create a test URL associated with the test user
        url = Url(long_url='https://example.com', 
                  short_url='https://darrkzero.pythonanywhere.com/abc123',
                  url_code="abc123",
                  user_id=user.id, 
                  title='Example Title')
        url.save()
        response = self.client.get(f"/url/{url.id}", headers={"Authorization": f"Bearer {access_token}"})

        assert response.status_code == HTTPStatus.OK

    #  test for QR code creation
    def test_create_qr_code(self):
        # Create a test user and generate JWT access token
        user = User( email='test@example.com',username="testUser", password_hash="password")
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(identity=user.email)  

        # Create a test URL associated with the test user
        url = Url(long_url='https://www.google.com/search?q=test&oq=test&aqs=chrome..69i57j0i271l2j69i60l3.1824j0j7&sourceid=chrome&ie=UTF-8', 
                  short_url='https://darrkzero.pythonanywhere.com/abc123',
                  url_code="abc123",
                  user_id=user.id, 
                  title='Example Title')
        url.save()
        response = self.client.post(f"/url/{url.id}/create_qrcode", headers={"Authorization": f"Bearer {access_token}"})

        assert response.status_code == HTTPStatus.OK
        assert response.content_type == 'image/png'
        

    #  test for deleting a user by user id 
    def test_delete_user(self):
         # Create a test user and generate JWT access token
        user = User( email='test@example.com',username="testUser", password_hash="password")
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(identity=user.email)  

        # Create a test URL associated with the test user
        url = Url(long_url='https://example.com', 
                  short_url='https://darrkzero.pythonanywhere.com/abc123',
                  url_code="abc123",
                  user_id=user.id, 
                  title='Example Title')
        url.save()
        response = self.client.delete(f"/url/user/{user.id}", headers={"Authorization": f"Bearer {access_token}"})

        assert response.status_code == HTTPStatus.OK


    #  test for getting url clicks  
    def test_url_clicks(self):
         # Create a test user and generate JWT access token
        user = User( email='test@example.com',username="testUser", password_hash="password")
        db.session.add(user)
        db.session.commit()
        # access_token = create_access_token(identity=user.email)  

        # Create a test URL associated with the test user
        url = Url(long_url='https://example.com', 
                  short_url='https://darrkzero.pythonanywhere.com/abc123',
                  url_code="abc123",
                  user_id=user.id, 
                  title='Example Title')
        url.save()
        response = self.client.get(f"/url/{url.url_code}/click")

        assert response.status_code == HTTPStatus.OK



