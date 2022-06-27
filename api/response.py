from rest_framework.response import Response
from .token import generate_anonymous_token


class AnonymousUserResponse(Response):
    def __init__(self, data=None, status=None, template_name=None,
                 headers=None, exception: bool = False, content_type=None):
        super().__init__(data, status, template_name, headers, exception, content_type)
        server_token, client_token = generate_anonymous_token()
        self.set_cookie('token', client_token)
