from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdmin, IsOwnerOrAdmin
from .serializers import SignupSerializer, TokenSerializer, UserSerializer

User = get_user_model()


class SendConfirmationCodeMixin:
    def send_confirmation_code(self, user):
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Сonfirmation Сode',
            f'Confirmation_Code: {confirmation_code}',
            settings.FROM_EMAIL_ADDRESS,
            [user.email],
        )
        return confirmation_code


class SignupView(APIView, SendConfirmationCodeMixin):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            if hasattr(serializer, 'existing_user'):
                existing_user = serializer.existing_user
                self.send_confirmation_code(existing_user)
                return Response(
                    {'email': existing_user.email,
                     'username': existing_user.username},
                    status=status.HTTP_200_OK
                )
            user = serializer.save()
            self.send_confirmation_code(user)
            return Response(
                {'email': user.email, 'username': user.username},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(TokenObtainPairView, SendConfirmationCodeMixin):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )

        if default_token_generator.check_token(
            user,
            serializer.validated_data['confirmation_code']
        ):
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
            })

        self.send_confirmation_code(user)
        return Response(
            {'detail': 'Код подтверждения неверный.'
             ' Новый код отправлен на почту.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    http_method_names = ['get', 'post', 'delete', 'patch']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if 'role' not in serializer.validated_data:
                serializer.validated_data['role'] = User.USER
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False,
            methods=['get', 'patch'], permission_classes=[IsOwnerOrAdmin])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
