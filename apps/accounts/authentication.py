import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        try:
            # Decode the Supabase JWT
            payload = jwt.decode(
                token, 
                settings.SUPABASE_JWT_SECRET, 
                algorithms=["HS256"], 
                audience="authenticated"
            )
            
            # 'sub' contains the user's UUID from Supabase Auth
            user_id = payload.get('sub')
            
            # Map the Supabase user to a Django User (or create if first time)
            user, created = User.objects.get_or_create(username=user_id)
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')
        except Exception as e:
            raise AuthenticationFailed('Authentication failed.')