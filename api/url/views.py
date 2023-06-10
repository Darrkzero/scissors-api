from flask import send_file
from flask_restx import Namespace, Resource, fields
from ..models.url import Url
from ..models.user import User
from ..utils import db
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
import string
import random
import requests
import qrcode

url_namespace = Namespace("url", description="name space for url")

# url model for inputing the link
url_model = url_namespace.model(
    "MainUrl",{
        "title": fields.String(required =True, description = "A url title"),
        "main_url": fields.String(required =True, description = "A url"),
    }
)

# Define a model for the URL customization request
url_customization_model = url_namespace.model('URLCustomization', {
    "title": fields.String(required =True, description = "A url title"),
    'custom_domain': fields.String(required=True, description='Custom domain name'),
    'url_path': fields.String(required=True, description='Custom URL path')
})

# view model for viewing the shortened url 
view_model = url_namespace.model(
    "ShortUrl",{
        "id":fields.Integer(),
        "title": fields.String(required =True, description = "A url title"),
        "long_url": fields.String(required =True, description = "A long url"),
        "short_url": fields.String(required =True, description = "A short url"),
        "url_code":  fields.String(required =True, description = "A url code"),
        "clicks":  fields.String(required =True, description = "url clicks"),
        "date_created": fields.String(required =True, description = "the shortened url creation date"),
    }
)


def shorten_url(long_url):
    # Generate a random short URL key
    letters = string.ascii_letters + string.digits
    short_key = ''.join(random.choice(letters) for _ in range(6))
    

    # Store the short URL in a database
    # Here, we'll return it
    return short_key

# Helper function to generate the QR code
def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_code_image = qr.make_image(fill_color="black", back_color="white")
    return qr_code_image

# Define the endpoint for creating short url
@url_namespace.route('/short_url')
class ShortUrl(Resource):
    @jwt_required()
    @url_namespace.expect(url_model)
    @url_namespace.marshal_with(view_model)
    @url_namespace.doc(description="""
            This endpoint is accessible to user. 
            It shorten the main url
            """)
    def post(self):
        """
        Create a shortened URL 
        """
        email = get_jwt_identity()
        data = url_namespace.payload

        current_user = User.query.filter_by(email=email).first()
        # shorten_url(data["main_url"])
        if data["main_url"]:
            try:  
                response = requests.head(data["main_url"])
                if response.status_code == requests.codes.ok:
                    url_db = Url.query.filter_by(long_url = data["main_url"]).first()

                    if url_db:
                        return url_db, HTTPStatus.OK
                    
                    else:
                        short_key = shorten_url(data["main_url"])
                        short_url = f"https://darrkzero.pythonanywhere.com/{short_key}"
                        new_url = Url(
                                url_code = short_key,
                                title = data["title"],
                                long_url = data["main_url"],
                                short_url = short_url,
                                user_id = current_user.id
                            )
                        try:
                            new_url.save()
                            return new_url, HTTPStatus.CREATED
                        
                        except:
                            db.session.rollback()
                            response = { 'message' : 'An error occurred'} 
                            return response , HTTPStatus.INTERNAL_SERVER_ERROR 
                    
            except requests.exceptions.RequestException:
                response=   {"message":"Invalid Url"}
                return response , HTTPStatus.BAD_REQUEST


# Define the endpoint for URL customization
@url_namespace.route('/customize_url')
class URLCustomizationResource(Resource):
    @jwt_required()
    @url_namespace.expect(url_customization_model)
    @url_namespace.marshal_with(view_model)
    def post(self):
        """
        Customize the shortened URL with a custom domain and URL path
        """
        email = get_jwt_identity()
        # Parse the request data
        data = url_namespace.payload
        custom_domain = data['custom_domain']
        url_path = data['url_path']

        current_user = User.query.filter_by(email=email).first()
        
        # Perform any necessary validation on the inputs
        
        # Generate the customized URL
        main_url = f'https://{custom_domain}/{url_path}'
        shortened_url = shorten_url(main_url)
        
        new_url = Url(
        long_url = main_url,
        short_url = shortened_url,
        user_id = current_user.id
                    )
        new_url.save()
        return new_url, HTTPStatus.CREATED


@url_namespace.route('/urls')
class GetAllUrl(Resource):
    # @jwt_required()
    @url_namespace.marshal_with(view_model)
    @url_namespace.doc(description="""
            This endpoint is accessible to everyboby. 
            retrieve all url
            """)
    def get(self):
        """
            Retrieve all url
        """        
        url_db = Url.query.all()

        return url_db, HTTPStatus.OK


# Define the endpoint for getting url by user id
@url_namespace.route('/urls/<int:user_id>')
class GetUrl(Resource):
    @jwt_required()
    @url_namespace.marshal_with(view_model)
    def get(self, user_id):
            """
                Get all url by user id
            """
            # email = get_jwt_identity()
            url_db = Url.query.filter_by(user_id=user_id).all()

            if url_db:
                return url_db, HTTPStatus.OK
            
            return {"message":"Invalid user id"}, HTTPStatus.BAD_REQUEST
    
    
# Define the endpoint for getting a single url by url id
@url_namespace.route('/<int:url_id>')
class UpdateUrl(Resource):
    @jwt_required()
    @url_namespace.doc(description="""
            This endpoint is accessible to only the user that created the url. 
            It updates a users url by url id
            """)
    def delete(self, url_id):
            """
                delete url by url id
            """
            email = get_jwt_identity()

            url_db = Url.query.filter_by(id=url_id).first()
            user_db = User.query.filter_by(email=email).first()
            if url_db:

                if url_db.user_id == user_db.id:
                    url_db.delete()

                    return {"message":"url successfully deleted"}, HTTPStatus.OK
                else:

                    return {"message":"Unauthorized user"}, HTTPStatus.OK
            
            return {"message":"Invalid url id"}, HTTPStatus.OK
        
    @url_namespace.marshal_with(view_model)
    def get(self, url_id):
        """
            Get url by url id
        """
            # email = get_jwt_identity()

        url_db = Url.query.filter_by(id=url_id).first()
        if url_db:

            return url_db, HTTPStatus.OK

        return {"message":"Invalid url id"}, HTTPStatus.BAD_REQUEST 



# Define the endpoint for QR code creation
@url_namespace.route('/<int:url_id>/create_qrcode')
class QRCodeCreationResource(Resource):
    @jwt_required()
    def post(self, url_id):
        """
        Create a QR code with the provided URL
        """
        # Parse the request data
        data = Url.query.filter_by(id=url_id).first()
        if data:
            url = data.long_url

            # Generate the QR code image
            qr_code_image = generate_qr_code(url)

            # Save the image to a temporary file
            temp_file_path = 'C:\\Users\\hp\\Documents\\flask-project\\scissors-api\\temp_qrcode.png'
            qr_code_image.save(temp_file_path)

            # Send the file as a response
            
            return send_file(temp_file_path, mimetype='image/png', as_attachment=True)
        
        return {"message":"Invalid url id"}, HTTPStatus.BAD_REQUEST


# Define the endpoint for getting a single user by user id
@url_namespace.route('/user/<int:user_id>')
class UpdateUrl(Resource):
    @jwt_required()
    @url_namespace.doc(description="""
            This endpoint is accessible to only the user by user id. 
            It updates a users url by url id
            """)
    def delete(self, user_id):
            """
                delete user by user id
            """
            email = get_jwt_identity()
            user_db = User.query.filter_by(id=user_id).first()
            url_dbs = Url.query.filter_by(user_id=user_id).all()
            
            if user_db.email == email:
                for url_db in url_dbs:
                    url_db.delete()
                user_db.delete()
                

                return {"message":"user successfully deleted"}, HTTPStatus.OK
            else:

                return {"message":"Unauthorized user"}, HTTPStatus.OK
            

@url_namespace.route('/<url_code>/click') 
class URLClickApiView(Resource): 
   @url_namespace.doc(description='Short url click count') 
   @url_namespace.marshal_with(view_model)   
   def get(self,url_code):
    #   print(url_code)
      url = Url.query.filter_by(url_code=url_code).first() 
      if not url:
         return {
            'message': 'Invalid url.'
         }, HTTPStatus.NOT_FOUND 
      url.clicks = url.clicks + 1
      try:
         url.save()
      except:
         pass
      return url , HTTPStatus.OK 