import email
from lib2to3.pgen2 import token
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from account.models import OTPToken, User

class RegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords didnt match.')
        return data

    def save(self):
        user = User(email = self.validated_data['email'],
                    username = self.validated_data['username']
                )
        password1 = self.validated_data['password1']
        password2 = self.validated_data['password2']

        if password1 != password2:
            raise serializers.ValidationError({'password': 'Passwords didnt match.'})
        user.set_password(password1)
        user.is_active = True
        user.is_email_verified = True
        user.save()
        return user


class AccountSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(User.objects.all())])
    username = serializers.CharField(validators=[UniqueValidator(User.objects.all())])

    def validate_username(self, value):
        if len(str(value)) < 5:
            raise serializers.ValidationError(f'Username must be at least 5 character.')
        return value
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'name', 'hide_email', 'display_pic']



class ChangePasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    def validate_current_password(self, value):
        user = self.context['user']
        # result = check_password(value, user.password)
        result = user.check_password(value)
        if not result:
            raise serializers.ValidationError(f'Incorrect Current Password')
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'The passwords didnt match'})
        return attrs

    class Meta:
        model = User
        fields = ['current_password', 'password1', 'password2']


class ResetPasswordSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'The passwords didnt match'})
        return attrs

    class Meta:
        model = User
        fields = ['password1', 'password2']
        

class ResetPasswordEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        try:
            account = User.objects.get(email=attrs['email'])
            print(account)
        except User.DoesNotExist:
                raise serializers.ValidationError('This email does not exist in our database.')
        return attrs

    class Meta:
        model = User
        fields = ['email']


class TokenResetpasswordSerializer(serializers.ModelSerializer):
    token = serializers.IntegerField()
    email = serializers.EmailField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    def validate_token(self, value):
        token = None
        try:
            token = OTPToken.objects.get(token=value)
        except OTPToken.DoesNotExist:
            raise serializers.ValidationError('Invalid token. Please enter correct one from your email.')
        if token.is_expired:
            raise serializers.ValidationError('Token expired. Request for a new token.')
        return value

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('User for that email not found. please enter a valid email.')
        return value

    def validate(self, attrs):
        try:
            token = OTPToken.objects.filter(token=attrs['token']).filter(user__email=attrs['email']).distinct()
        except OTPToken.DoesNotExist:
            raise serializers.ValidationError('Invalid email or token. Please enter correct token from your email.')
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'The passwords didnt match'})
        return attrs

    class Meta:
        model = OTPToken
        fields = ['token', 'email', 'password1', 'password2']
