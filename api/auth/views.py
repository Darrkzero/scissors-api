from flask_restx import Namespace, Resource, fields
from flask import request, jsonify,Flask, render_template, redirect, url_for
from ..models.user import User
from ..utils import db
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import random
import string


auth_namespace = Namespace("auth", description="name space for authentication")

# signup model for both admin and teachers
signup_model = auth_namespace.model(
    "SignupUser",{
        "username": fields.String(required =True, description = "A name"),
        "email": fields.String(required =True, description = "An email"),
        "password":fields.String(required =True, description = "A password")
    }
)

view_model = auth_namespace.model(
    "User",{
        "id":fields.Integer(),
        "username": fields.String(required =True, description = "A name"),
        "email": fields.String(required =True, description = "An email"),
        "password_hash":fields.String(required =True, description = "A password"),
    }
)

# login model for all users
login_model = auth_namespace.model(
    "LoginStudent",{
        "email": fields.String(required =True, description = "An email"),
        "password":fields.String(required =True, description = "A password")
    }
)

password_model  = auth_namespace.model(
    "Password",{
        "old_password": fields.String(required =True, description = "old password"),
        "new_password":fields.String(required =True, description = "new password")
    })


# endpoint for registering user
@auth_namespace.route("/signup")
class SignUp(Resource):

    @auth_namespace.expect(signup_model)
    @auth_namespace.marshal_with(view_model)
    @auth_namespace.doc("Register admin or teacher")
    def post(self):
        """
        Signup a user
        """
        data = request.get_json()
        new_user = User(
            username = data.get("username"),
            email = data.get("email"),
            password_hash = generate_password_hash(data.get("password"))
        )
        new_user.save()
        return new_user,HTTPStatus.CREATED
    


@auth_namespace.route("/login")
class Login(Resource):
    @auth_namespace.expect(login_model)
    def post(self):
        """
        Login a user
        """
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")
        user = User.query.filter_by(email=email).first()
        
        if user is not None and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity = user.email)
            refresh_token = create_refresh_token(identity = user.email)
            response = {
                "access_token":access_token,
                "refresh_token":refresh_token
            }

            return response, HTTPStatus.CREATED


@auth_namespace.route("/refresh")
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        username= get_jwt_identity()
        access_token = create_access_token(identity=username)
        return{"access_token": access_token}, HTTPStatus.OK
    
@auth_namespace.route("/reset_password")
class Refresh(Resource):
    @jwt_required()
    @auth_namespace.expect(password_model)
    def patch(self):
        """
        change password
        """
        email= get_jwt_identity()

        data = request.get_json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        user = User.query.filter_by(email=email).first()
        if user is not None and check_password_hash(user.password_hash, old_password):
            user.password_hash = generate_password_hash( new_password)
            db.session.commit()

        return{"message":"password changed successfully"}, HTTPStatus.OK