from .api.auth_api import SignupApi, LoginApi


def initialize_routes(api):
    api.add_resource(SignupApi, "/api/signup")
    api.add_resource(LoginApi, "/api/login")
