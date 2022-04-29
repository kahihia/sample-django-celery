from django import forms
from django.contrib.auth import password_validation

from account.models import User


class LoginForm(forms.ModelForm):
    
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'autocomplete': 'email'}),
    )
    password = forms.CharField(label="Password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'Invalid email or password.')
        return email

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) > 0:
            raise forms.ValidationError('Something went wrong.')
        return text

    class Meta:
        model = User
        fields = ('email', 'password', 'text')
        widgets = {
            'text': forms.HiddenInput(attrs={'type': 'hidden', 'class': ''}),
        }


class RegistrationForm(forms.ModelForm):

    password1 = forms.CharField(label="Password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html()
    )
    password2 = forms.CharField(label="Password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'This email is already registered. Login to continue.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'This username is taken. Try a different one')
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError(f'The two passwords must be same.')
        return password2

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) > 0:
            raise forms.ValidationError('Something went wrong.')
        return text

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password1'))
        user.is_email_verified = True
        if commit:
            user.save()
        return user


    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2', 'text')
        widgets = {
            'text': forms.HiddenInput(attrs={'type': 'hidden', 'class': ''}),
        }
        help_texts = {
            'username': 'Better to use your email without "@gmail.com".',
        }


class UserUpdateForm(forms.ModelForm):

    def clean_display_pic(self):
        display_pic = self.cleaned_data.get('display_pic')
        extension = str(display_pic).split('.')[-1]
        if extension not in ['jpeg', 'jpg', 'png']:
            raise forms.ValidationError(f'Invalid image type.')
        return display_pic


    class Meta:
        model = User
        fields = ('display_pic', 'email', 'username', 'name', 'hide_email')
