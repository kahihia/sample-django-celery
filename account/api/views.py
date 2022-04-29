from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import send_mail
from django.conf import settings

from django.shortcuts import redirect
from django.contrib import messages

from account.models import OTPToken, User
from account.tokens import account_activation_token
from account.api.serializer import RegistrationSerializer, AccountSerializer, ChangePasswordSerializer, ResetPasswordEmailSerializer, ResetPasswordSerializer, TokenResetpasswordSerializer


@api_view(['POST', ])
def registration_api_view(request, *args, **kwargs):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data={
            'email': request.data['email'], 
            'username': request.data['username'], 
            'password1': request.data['password1'], 
            'password2': request.data['password2']
        })
        redirect_link = request.data['redirect_link']

        try:
            if serializer.is_valid():
                user = serializer.save()

                site = get_current_site(request)
                subject = 'Activate Your Account.'
                message = render_to_string('account/api/api_account_activation_email.html', {
                    'user': user,
                    'domain': site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.id)),
                    'token': account_activation_token.make_token(user),
                    'redirect_link': redirect_link
                })
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email, ], fail_silently=False)
                return Response({'message': 'An activation email is sent to your email. \nPlease Check your email to login.'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Something went wrong. Please register again from begning.'}, status=status.HTTP_400_BAD_REQUEST)


def account_verify_api_view(request, uidb64, token, redirect_link, *args, **kwargs):
    try:
        user_id = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True
        user.save()
        
    if redirect_link != '':
        redirect_link = redirect_link.replace('--','/')
        return redirect(f'http://{redirect_link}')
    else:
        messages.success('Account activated successfully.')
        return redirect('account:account-home')



class AccountDetailAPIView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        if user != request.user:
            return Response({'message': 'Illegal Access Attempt!'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = AccountSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        user = request.user
        if user != request.user:
            return Response({'message': 'Illegal Access Attempt!'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = AccountSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format = None):
        user = request.user
        if user != request.user:
            return Response({'message': 'Illegal Access Attempt!'}, status=status.HTTP_401_UNAUTHORIZED)
        elif user == request.user:
            user.delete()
            return Response({'message': 'Account deleated successfully.'}, status=status.HTTP_200_OK)
            

@api_view(['POST',])
@permission_classes([IsAuthenticated])
def password_change_api_view(request):
    user = request.user
    if request.method == 'POST':
        serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            password = request.data['password1']
            user.set_password(password)
            user.save()
            return Response({'message': 'Password changed successfully.'},status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['post',])
def password_reset_request_api_view(request):
    serializer = ResetPasswordEmailSerializer(data= {
        'email': request.data['email'], 
    })
    redirect_link = request.data['redirect_link']
    if serializer.is_valid():

        user = User.objects.get(email=request.data['email'])

        try:
            site = get_current_site(request)
            subject = 'Reset Your password'
            message = render_to_string('account/api/api_password_reset_email.html', {
                'user': user,
                'domain': site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': account_activation_token.make_token(user),
                'redirect_link': redirect_link
            })
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email,], fail_silently=False)
            return Response({'message': 'A Password reset mail is sent to your email. \nPlease Check your email to login.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Something went wrong. \nPlease retry.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def password_reset_verify_api_view(request, uidb64, token, redirect_link, *args, **kwargs):
    try:
        user_id = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True
        user.save()
        
    redirect_link = redirect_link.replace('--','/')
    return redirect(f'http://{redirect_link}/{user.id}')


@api_view(['post',])
def password_reset_api_view(request, id):
    serializer = ResetPasswordSerializer(data={
        'password1': request.data['password1'],
        'password2': request.data['password2'],
    })
    if serializer.is_valid():
        user = User.objects.get(id=id)
        if user:
            password = request.data['password1']
            user.set_password(password)
            user.save()
            return Response({'message': 'Password reset success'}, status=status.HTTP_200_OK)
        else:
            return Response({'non_field_errors': 'User not found. Something went wrong while resetting password'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['post',])
@permission_classes([IsAuthenticated])
def account_search_api_view(request):
    user = request.user
    query = request.data['userQuery']
    users = User.objects.filter(username__icontains=query).filter(email__icontains=query).exclude(email=user.email).distinct()
    if users:
        serializer = AccountSerializer(users, many=True)
        return Response(serializer.data)
    else:
        return Response({'message': 'No users found.'})


@api_view(['post',])
def password_reset_request_token_api_view(request):
    serializer = ResetPasswordEmailSerializer(data= {
        'email': request.data['email'], 
    })
    if serializer.is_valid():

        user = User.objects.get(email=request.data['email'])
        otp_token = OTPToken.objects.create(user=user)

        try:
            subject = 'Reset Your password'
            message = render_to_string('account/api/api_token_password_reset_email.html', {
                'user': user,
                'token': otp_token.token,
            })
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email,], fail_silently=False)
            return Response({'message': 'A Password reset mail with token is sent to your email.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Something went wrong. \nPlease retry.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['post',])
def password_reset_token_api_view(request):
    serializer = TokenResetpasswordSerializer(data={
        'token': request.data['token'],
        'email': request.data['email'],
        'password1': request.data['password1'],
        'password2': request.data['password2'],
    })
    if serializer.is_valid():
        user = User.objects.get(email=request.data['email'])
        if user:
            password = request.data['password1']
            user.set_password(password)
            user.save()
            return Response({'message': 'Password reset success'}, status=status.HTTP_200_OK)
        else:
            return Response({'non_field_errors': 'User not found. Something went wrong while resetting password'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
