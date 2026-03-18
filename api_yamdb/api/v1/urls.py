from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    signup,
    TokenObtainView,
    UserViewSet,
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet,
)

app_name = 'api_v1'

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('auth/signup/', signup, name='signup'),
    path('auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path(
        'titles/<int:title_id>/reviews/',
        ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='review-list',
    ),
    path(
        'titles/<int:title_id>/reviews/<int:review_id>/',
        ReviewViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='review-detail',
    ),
    path(
        'titles/<int:title_id>/reviews/<int:review_id>/comments/',
        CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='comment-list',
    ),
    path(
        'titles/<int:title_id>/reviews/<int:review_id>/'
        'comments/<int:comment_id>/',
        CommentViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='comment-detail',
    ),
    path('', include(router_v1.urls)),
]
