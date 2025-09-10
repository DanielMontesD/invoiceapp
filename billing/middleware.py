"""
Custom middleware for basic authentication.
"""
from django.http import HttpResponse
from django.contrib.auth import authenticate
import base64


class BasicAuthMiddleware:
    """
    Middleware to add basic HTTP authentication to the entire site.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip authentication for static files and admin
        if (request.path.startswith('/static/') or 
            request.path.startswith('/admin/') or
            request.path.startswith('/favicon.ico')):
            return self.get_response(request)

        # Check if user is already authenticated
        if request.user.is_authenticated:
            return self.get_response(request)

        # Check for basic auth header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Basic '):
            try:
                # Decode the base64 credentials
                credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
                username, password = credentials.split(':', 1)
                
                # Authenticate user
                user = authenticate(request, username=username, password=password)
                if user and user.is_active:
                    request.user = user
                    return self.get_response(request)
            except:
                pass

        # Return 401 Unauthorized
        response = HttpResponse('Authentication required', status=401)
        response['WWW-Authenticate'] = 'Basic realm="Invoice App"'
        return response
