from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token

from account.api.views import (
    registration_api_view, 
    account_verify_api_view,
    account_search_api_view,
    password_change_api_view,

    password_reset_request_token_api_view,
    password_reset_token_api_view,

    password_reset_request_api_view,
    password_reset_verify_api_view,
    password_reset_api_view,

    AccountDetailAPIView
)


app_name = 'account_api'


urlpatterns = [
    path('register/', registration_api_view, name='api-register'),
    path('account_verify/<uidb64>/<token>/<redirect_link>/', account_verify_api_view, name='api-account-verify'),
    path('login/', obtain_auth_token, name='api-login'),
    path('account/', AccountDetailAPIView.as_view(), name='api-account-detail'),
    path('account_search/', account_search_api_view, name='api-account-search'),

    path('password_change/', password_change_api_view, name='api-password-change'),

    path('password_reset_request_token/', password_reset_request_token_api_view, name='api-password-reset-request'),
    path('password_reset_token/', password_reset_token_api_view, name='api-password-reset-token'),

    path('password_reset_request/', password_reset_request_api_view, name='api-password-reset-request'),
    path('password_reset_verify/<uidb64>/<token>/<redirect_link>/', password_reset_verify_api_view, name='api-password-reset-verify'),
    path('password_reset/<id>/', password_reset_api_view, name='api-password-reset'),
]


