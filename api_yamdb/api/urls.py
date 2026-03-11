from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path(
        'v1/titles/<int:title_id>/reviews/',
        ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='review-list',
    ),
    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/',
        ReviewViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='review-detail',
    ),
    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/comments/',
        CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='comment-list',
    ),
    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/comments/<int:comment_id>/',
        CommentViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='comment-detail',
    ),
    path('v1/', include(router.urls)),
]
