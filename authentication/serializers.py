from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.core.mail import send_mail
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data, username=validated_data["email"])


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(request=self.context.get('request'), username=data['email'], password=data['password'])
        if user and user.is_active:
            return {'user': user}
        raise AuthenticationFailed("Invalid credentials")



class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("No user is associated with this email address.")

    def send_password_reset_email(self, user):
        token = default_token_generator.make_token(user)
        reset_url = f"http://localhost:3000/reset-password/{token}/"
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_url}",
            from_email="noreply@bookexchange.com",
            recipient_list=[user.email],
        )



class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters.")
        return value