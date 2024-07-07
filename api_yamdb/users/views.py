from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsAdmin, IsOwnerOrAdmin
from .serializers import SignupSerializer, TokenSerializer, UserSerializer


User = get_user_model()


class EmailTokenMixin:
    def send_token_email(self, user, token_type='confirmation'):
        if token_type == 'confirmation':
            subject = 'Ваш код подтверждения'
            message = (
                f'Ваш код подтверждения: '
                f'{default_token_generator.make_token(user)}'
            )
        elif token_type == 'new_confirmation':
            subject = 'Ваш новый код подтверждения'
            message = (
                f'Ваш новый код подтверждения: '
                f'{default_token_generator.make_token(user)}'
            )
        send_mail(
            subject,
            message,
            settings.FROM_EMAIL_ADDRESS,
            [user.email],
        )


class SignupView(EmailTokenMixin, APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']

            existing_user = (
                User.objects.filter(email=email).first()
                or User.objects.filter(username=username).first()
            )

            if existing_user:
                if (existing_user.email == email
                        and existing_user.username == username):
                    token = RefreshToken.for_user(existing_user)
                    return Response(
                        {'token': str(token.access_token)},
                        status=status.HTTP_200_OK
                    )
                elif existing_user.email == email:
                    return Response(
                        {'error': 'Email уже существует'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                elif existing_user.username == username:
                    return Response(
                        {'error': 'Имя пользователя уже занято'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            user = User.objects.create(email=email, username=username)
            self.send_token_email(user)
            return Response(
                {'email': user.email, 'username': user.username},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(EmailTokenMixin, APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = get_object_or_404(
                    User,
                    username=serializer.validated_data['username']
                )
            except User.DoesNotExist:
                return Response(
                    {'username': 'Имя пользователя не найдено'},
                    status=status.HTTP_404_NOT_FOUND
                )
            if default_token_generator.check_token(
                user,
                serializer.validated_data['confirmation_code']
            ):
                refresh = RefreshToken.for_user(user)
                return Response(
                    {'token': str(refresh.access_token)},
                    status=status.HTTP_200_OK
                )
            self.send_token_email(user, token_type='new_confirmation')
            return Response(
                {'confirmation_code': 'Неверный код подтверждения. '
                 'Новый код отправлен.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    http_method_names = ['get', 'post', 'delete', 'head', 'options', 'patch']

    def check_email_unique(self, email):
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                'Этот адрес электронной почты уже используется'
            )

    def check_username_unique(self, username):
        if User.objects.filter(username=username).exists():
            raise ValidationError('Это имя пользователя уже используется')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.check_username_unique(
                    serializer.validated_data['username']
                )
            except ValidationError as error:
                return Response({'username': str(error)},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                self.check_email_unique(serializer.validated_data['email'])
            except ValidationError as error:
                return Response({'email': str(error)},
                                status=status.HTTP_400_BAD_REQUEST)
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
