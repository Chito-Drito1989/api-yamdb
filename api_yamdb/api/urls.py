from django.urls import include, path
from .views import signup, TokenObtainView

app_name = 'api'

auth_urlpatterns = [
    path('signup/', signup, name='signup'),
]

urlpatterns = [
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', TokenObtainView.as_view(), name='token_obtain'),
]