from ez_assignment.settings import SECRET_KEY
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


def create_jwt_pair_for_user(user: User):
    refresh = RefreshToken.for_user(user)
    refresh['user_id'] = f"{user.id}"
    tokens = {"access": str(refresh.access_token), "refresh": str(refresh)}

    return tokens
