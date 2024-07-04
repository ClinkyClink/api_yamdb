from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import UserSerializer, SignupSerializer, TokenSerializer

User = get_user_model()


class SignupView(APIView):
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
                        {'token': str(token)},
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
            confirmation_code = default_token_generator.make_token(user)
            send_mail(
                'Ваш код подтверждения',
                f'Ваш код подтверждения: {confirmation_code}',
                'from@example.com',
                [user.email],
            )
            return Response(
                {'email': user.email, 'username': user.username},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(
                    username=serializer.validated_data['username']
                )
            except User.DoesNotExist:
                return Response(
                    {'username': 'Пользователь не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )

            confirmation_code = serializer.validated_data['confirmation_code']
            if default_token_generator.check_token(user, confirmation_code):
                return Response(
                    {'token': 'Ваше сообщение с токеном здесь'},
                    status=status.HTTP_200_OK
                )
            return Response(
                {'confirmation_code': 'Неверный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
