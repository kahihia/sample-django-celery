from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import send_mail
from django.conf import settings

from account.models import User
from account.forms import LoginForm, RegistrationForm, UserUpdateForm
from account.tokens import account_activation_token

# import requests


def login_view(request, *args, **kwargs):
    context = {}
    user = request.user

    if user.is_authenticated:
        messages.info(request, f'You are already logged in...')
        return redirect('celery_tracker:celery_tracker')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        # try:
        #     recaptcha_response = request.POST.get('g-recaptcha-response')
        #     data = {
        #         'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        #         'response': recaptcha_response
        #     }
        #     recaptcha_response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        #     result = recaptcha_response.json()
        #     if not result['success']:
        #         messages.warning('Recaptcha validation failed.')
        #         return redirect('account:login')
        # except Exception as e:
        #     messages.warning('Something went wrong. Please login again.')
        #     return redirect('account:home')

        if form.is_valid:
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, email=email, password=password)
            if user:
                if user.is_email_verified:
                    login(request, user)
                    return redirect('celery_tracker:celery_tracker')

                if not user.is_active:
                    user.is_active = True
                    user.save()

#                 if not user.is_email_verified:
#                     try:
#                         site = get_current_site(request)
#                         subject = 'Activate Your Account.'
#                         message = render_to_string('account/email/account_activation_email.html', {
#                             'user': user,
#                             'domain': site.domain,
#                             'uid': urlsafe_base64_encode(force_bytes(user.id)),
#                             'token': account_activation_token.make_token(user),
#                         })
#                         send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email, ], fail_silently=False)
#                     except Exception as e:
#                         messages.info(request, f'Something went wrong while sending verification email. Please refresh the page and login again.')
#                         return render(request, 'account/email/account_verified.html', context)

#                     messages.info(request, f'An email with verification link is sent to your Email ID. Verify Your account before login.')
#                     return render(request, 'account/email/account_verified.html', context)
            else:
                messages.warning(request, f'Something went wrong.')
                context['form'] = LoginForm()
        else:
            messages.warning(request, f'Invalid email or password. Please enter correct credentials.')
            context['form'] = LoginForm()

    if request.method == 'GET':
        context['form'] = LoginForm()
        context['GOOGLE_RECAPTCHA_SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
    return render(request, 'account/login.html', context)


def logout_view(request, *args, **kwargs):
    logout(request)
    messages.info(request, f'Logged Out...')
    return redirect('celery_tracker:celery_tracker')


def register_view(request, *args, **kwargs):
    context = {}
    user = request.user

    if user.is_authenticated:
        messages.info(
            request, f'You are already logged in with an account {user.username}. Same person cannot have multiple accounts...')
        return redirect('celery_tracker:celery_tracker')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

#             try:
#                 site = get_current_site(request)
#                 subject = 'Activate Your Account.'
#                 message = render_to_string('account/email/account_activation_email.html', {
#                     'user': user,
#                     'domain': site.domain,
#                     'uid': urlsafe_base64_encode(force_bytes(user.id)),
#                     'token': account_activation_token.make_token(user),
#                 })
#                 send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email, ], fail_silently=False)
#             except Exception as e:
#                 messages.success(request, f'There was a problem while sending verification email. Please proceed to login.')
#                 return render(request, 'account/email/account_verified.html', context)

#             messages.success(request, f'An email with verification link is sent to your Email ID. Verify Your account before login.')
#             return render(request, 'account/email/account_verified.html', context)

            messages.success(request, f'Account created successfully.')
            return redirect('account:login')
        else:
            messages.warning(request, f'Error...!')
            context['form'] = form

    if request.method == 'GET':
        context['form'] = RegistrationForm()
    return render(request, 'account/register.html', context)


def account_verify_view(request, uidb64, token, *args, **kwargs):
    try:
        user_id = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True
        user.save()
        login(request, user)
        messages.success(request, f'An account for {user.username} created successfully.')
        return redirect('celery_tracker:celery_tracker')
    else:
        messages.info(request, f'Something went wrong.')
        return redirect('celery_tracker:celery_tracker')


def account_view(request, *args, **kwargs):
    context = {}
    user = request.user

    if not user.is_authenticated:
        messages.warning(request, f'You must login to view someones profile.')
        return redirect('account:login')

    user_id = kwargs.get('user_id')
    try:
        account = User.objects.get(id=user_id)
        context['user'] = account
        if account == user:
            context['is_self'] = True
    except User.DoesNotExist:
        messages.warning(request, f'Not a valid account.')
    return render(request, 'account/account.html', context)


def account_update_view(request, *args, **kwargs):
    context = {}
    user = request.user

    if not user.is_authenticated:
        messages.warning(request, f'You must login to update profile.')
        return redirect('account:login')

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated...!')
            return redirect('account:account', user_id=user.id)
        else:
            messages.info(request, f'Error...!')
            context['form'] = form
            
    if request.method == 'GET':
        form = UserUpdateForm(instance=user)
        context['form'] = form
    return render(request, 'account/account_update.html', context)


def account_search_view(request, *args, **kwargs):
    context = {}
    user = request.user

    if not user.is_authenticated:
        messages.warning(request, f'You must login to search someones profile.')
        return redirect('account:login')

    if request.method == 'GET':
        query = request.GET.get('userQuery')
        if len(query) > 0:
            users = User.objects.filter(username__icontains=query).filter(email__icontains=query).filter(is_active=True).exclude(email=user.email).distinct()
            context['users'] = users
    return render(request, 'account/account_search.html', context)

def account_deactivate_view(request, *args, **kwargs):
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()
        messages.info(request, 'Your account has been deactivated. Proceed to login to reactivate the account')
        return redirect('account:logout')

    return render(request, 'account/account_deactivate.html')

def account_delete_view(request, *args, **kwargs):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.warning(request, 'Your account has been deleted successfully.')
        return redirect('celery_tracker:celery_tracker')

    return render(request, 'account/account_delete.html')
