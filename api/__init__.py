from flask import Flask
from .auth.views import auth_namespace
from .url.views import url_namespace
from flask_restx import Api
from .config.config import config_dict
from .utils import db
from .models.user import User
from .models.url import Url
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager


# initialization of flask_restx
def create_app(config = config_dict['dev']):
    app= Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    

    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT token to the header with ** Bearer &lt;JWT&gt; ** token to authorize"
        }
    }

    api = Api(
        app,
        title='Student Management API',
        description='A simple Student Management REST API service',
        authorizations=authorizations,
        security='Bearer Auth'
        )
    api.add_namespace(auth_namespace)
    api.add_namespace(url_namespace)
    
    @app.shell_context_processor
    def make_shell_context():
        return{
            "db":db,
            "User":User,
            "Url":Url,
        }

    

    return app