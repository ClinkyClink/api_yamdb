"""Маршруты приложения api."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet, TitleViewSet, GenreViewSet, CategoryViewSet, CommentViewSet
from users.views import SignupView, TokenView, UserViewSet, UserMeViewSet

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='user')
router_v1.register(
    r'^titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review'
)
router_v1.register(
    r'^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register('titles', TitleViewSet, basename='title')

urlpatterns = [
    path('v1/auth/signup/', SignupView.as_view(), name='signup'),
    path('v1/auth/token/', TokenView.as_view(), name='token'),
    path('v1/users/me/', UserMeViewSet.as_view({'get': 'me', 'patch': 'me'}), name='me'),
    path('v1/', include(router_v1.urls)),
]
