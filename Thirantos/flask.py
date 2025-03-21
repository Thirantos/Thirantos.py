from functools import wraps
from flask import request, Response
from .authenticator import Authenticator

def secure(auth: Authenticator):
    """
    Decorator to secure a Flask route with token-based authentication.

    Args:
        auth (Authenticator): An instance of an Authenticator to validate tokens.

    Returns:
        function: The decorated function with authentication.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.headers.get("token")  # Safely get the token
            if not token or not auth.use_token(token):
                return Response("Unauthorized", status=401)  # Unauthorized if token is missing or invalid
            return func(*args, **kwargs)  # Proceed if authenticated
        return wrapper
    return decorator

def parameters(**params):
    """
    Decorator to parse and validate query parameters for a Flask route.

    Args:
        **params: Default values for the query parameters.

    Returns:
        function: The decorated function with parsed parameters.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            p: dict[str, any] = {}
            for k, v in params.items():
                try:
                    p[k] = type(v)(request.args.get(k) or v)
                except ValueError:
                    return Response(f"Invalid parameter {k}", status=400)
            return func(*args, **kwargs, p=p)
        return wrapper
    return decorator

def wrap_data(data) -> dict[str, any]:
    """
    Wrap data in a dictionary with a count of the results.

    Args:
        data (list): The data to wrap.

    Returns:
        dict: A dictionary containing the count and the results.
    """
    return {
        "count": len(data),
        "results": data
    }