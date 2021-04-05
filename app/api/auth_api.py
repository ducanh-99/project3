from flask import request
from app.model import User
from flask_restful import Resource
from flask_login import login_user
from .. import db


class LoginApi(Resource):
    def get(self):
        email = request.args.get("email")
        password = request.args.get("password")
        user = User.query.filter_by(email=email).first()
        print(user)
        if user is not None and user.verify_password(password):
            login_user(user)
            return {'message': "Login success"}, 200


class SignupApi(Resource):
    def get(self):
        user = User(email=request.args.get("email"),
                    username=request.args.get("username"),
                    password=request.args.get("password"))
        db.session.add(user)
        db.session.commit()
