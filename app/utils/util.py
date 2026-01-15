from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def encode_token(customer_id):
    """
    Generate a JWT token for a customer.
    """
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc),
        "sub": str(customer_id)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def token_required(f):
    """
    Decorator to protect routes and extract customer_id from token.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            customer_id = int(decoded["sub"])
        except JWTError:
            return jsonify({"message": "Invalid or expired token!"}), 401

        return f(customer_id, *args, **kwargs)

    return decorated

def mechanic_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check for Authorization header
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_mechanic_id = payload.get("mechanic_id")
        except:
            return jsonify({"message": "Token is invalid or expired"}), 403
        return f(current_mechanic_id, *args, **kwargs)
    return decorated

