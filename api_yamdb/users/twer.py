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

            if existing_user and not existing_user.is_active:
                # Resend confirmation code if user exists but is not active
                confirmation_code = default_token_generator.make_token(existing_user)
                send_mail(
                    'Ваш код подтверждения',
                    f'Ваш код подтверждения: {confirmation_code}',
                    settings.FROM_EMAIL_ADDRESS,
                    [existing_user.email],
                )
                return Response(
                    {'detail': 'Confirmation code has been resent.'},
                    status=status.HTTP_200_OK
                )

            elif existing_user and existing_user.is_active:
                # User exists and is already verified
                return Response(
                    {'detail': 'User is already registered and verified.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create a new user if no existing user found
            user = User.objects.create(email=email, username=username)
            confirmation_code = default_token_generator.make_token(user)
            send_mail(
                'Ваш код подтверждения',
                f'Ваш код подтверждения: {confirmation_code}',
                settings.FROM_EMAIL_ADDRESS,
                [user.email],
            )
            return Response(
                {'detail': 'Confirmation code has been sent.'},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)