from django.urls import include, path
from .views import signup

app_name = 'api'

auth_urlpatterns = [
    path('signup/', signup, name='signup'),
]

urlpatterns = [
    path('v1/auth/', include(auth_urlpatterns)),
]