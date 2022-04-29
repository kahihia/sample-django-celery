from django.urls import path, reverse_lazy

from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,

    PasswordChangeView,
    PasswordChangeDoneView,
)

from account.views import (
    login_view,
    logout_view,
    register_view,
    account_verify_view,
    account_view,
    account_update_view,
    account_search_view,
    account_deactivate_view,
    account_delete_view
)


app_name = 'account'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('account_verify/<uidb64>/<token>/',
         account_verify_view, name='account-verify'),

    path('account/<user_id>/', account_view, name='account'),
    path('account_update/', account_update_view, name='account-update'),
    path('account_search/', account_search_view, name='account-search'),
    path('account_deactivate/', account_deactivate_view, name='account-deactivate'),
    path('account_delete/', account_delete_view, name='account-delete'),


    path('password_reset/', PasswordResetView.as_view(
        template_name='account/password/password_reset.html',
        email_template_name='account/password/password_reset_email.html',
        success_url=reverse_lazy('account:password-reset-done')),
        name='password-reset'
    ),
    path('password_reset_done/', PasswordResetDoneView.as_view(
        template_name='account/password/password_reset_done.html'),
        name='password-reset-done'
    ),
    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='account/password/password_reset_confirm.html',
        success_url=reverse_lazy('account:password-reset-complete')),
        name='password-reset-confirm'
    ),
    path('password_reset_complete/', PasswordResetCompleteView.as_view(
        template_name='account/password/password_reset_complete.html'),
        name='password-reset-complete'
    ),

    path('password_change/', PasswordChangeView.as_view(
        template_name='account/password/password_change.html',
        success_url=reverse_lazy('account:password-change-done')),
        name='password-change'
    ),
    path('password_change_done/', PasswordChangeDoneView.as_view(
        template_name='account/password/password_change_done.html'),
        name='password-change-done'
    ),
]
