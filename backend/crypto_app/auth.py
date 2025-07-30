import jwt
import datetime
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from django.http import JsonResponse


def generate_service_token():
    payload = {
        "service": "crm_core",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=20),
        "iat": datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token



User = get_user_model()

def jwt_auth_required(view_func):
    @wraps(view_func)
    async def _wrapped_view(request, *args, **kwargs):
        from .models import User


        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return JsonResponse({'detail': 'Unauthorized'}, status=401)
        token = auth.split(' ')[1]
        try:
            UntypedToken(token)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("user_id")
            user = await User.get(id=user_id)
            request.user = user
        except (TokenError, InvalidToken):
            return JsonResponse({'detail': 'Expired / Invalid token or user does not exist'}, status=401)

        return await view_func(request, *args, **kwargs)
    return _wrapped_view


def service_jwt_auth_required(view_func):
    """
    Decorator to enforce service-level JWT authentication for internal microservice communication.
    """
    @wraps(view_func)
    async def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse({"detail": "Authorization header missing or invalid"}, status=401)
        
        token = auth_header[7:]

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            print(f"Service call from: {payload.get('service')}")

            # Optional: You can validate a service name/role
            service_name = payload.get("service")
            if service_name not in {"crm_emailgen", "crm_scrapper", "crm_notification", "crm_matchmaker"}:
                return JsonResponse({"detail": "Unauthorized service"}, status=403)

            # Store service identity if needed
            request.service = service_name
            
            return await view_func(request, *args, **kwargs)
        
        except jwt.ExpiredSignatureError:
            return JsonResponse({"detail": "Token has expired"}, status=401)
        except jwt.InvalidTokenError as e:
            return JsonResponse({"detail": f"Invalid token: {str(e)}"}, status=401)
    
    return _wrapped_view







