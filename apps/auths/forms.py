from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
)
from auths.models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = (
            'email',
        )


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = (
            'email',
        )


class CustomUserForm(forms.ModelForm):
    email = forms.EmailField(
        label='Почта'
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль'
    )

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'password',
        )
