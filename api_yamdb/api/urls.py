"""Маршруты приложения api."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet, TitleViewSet, GenreViewSet, CategoryViewSet

router_v1 = DefaultRouter()
router_v1.register(
    r'^titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review'
)
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register('titles', TitleViewSet, basename='title')

urlpatterns = [
    path('v1/', include(router_v1.urls))
]
