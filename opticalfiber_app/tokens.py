from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    
    # Add custom claims
    refresh['company_id'] = user.company.pk
    refresh['role'] = user.role
    refresh['name'] = user.name
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'access_token_expiration': refresh.access_token['exp'],
    }
