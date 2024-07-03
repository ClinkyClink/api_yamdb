from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import SignupView, TokenView, UserViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/auth/signup/', SignupView.as_view(), name='signup'),
    path('v1/auth/token/', TokenView.as_view(), name='token'),
    path('v1/', include(router.urls)),
]
