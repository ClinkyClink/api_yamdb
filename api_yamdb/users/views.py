from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.decorators import action

from .serializers import UserSerializer, SignupSerializer, TokenSerializer
from .permissions import IsAdmin, IsAdminOrReadOnly, IsOwnerOrAdminOrReadOnly, IsOwnerOrAdmin
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
                    {'username': 'User not found'},
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
            return Response(
                {'confirmation_code': 'Invalid confirmation code'},
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

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdmin]
        elif self.action in ['retrieve']:
            self.permission_classes = [IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if 'role' not in serializer.validated_data:
                serializer.validated_data['role'] = User.USER
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsOwnerOrAdmin])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
