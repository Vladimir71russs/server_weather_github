import requests
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

from users.models import NotificationSetting


# Форма регистрации
class UserRegistrationForm(UserCreationForm): #от UserCreationForm идут 'username''password1', 'password2'
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),  # Оформление каждого поля
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    # Проверяем почту на уникальность
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже используется!")
        return email

    # Убираем подсказки для паролей
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['username'].error_messages = {'required': None}
        self.fields['password1'].help_text = None  # Убираем подсказку для password1
        self.fields['password2'].help_text = None  # Убираем подсказку для password2


# Форма для авторизации
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'placeholder': 'Имя пользователя', 'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'placeholder': 'Пароль', 'class': 'form-control'}))


# Форма для редактирования профиля
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None  # Убираем help_text для username

    # Проверка уникальность имени пользователя
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise ValidationError("Это имя пользователя уже занято.")
        return username

    # Проверка уникальность почты
    def clean_email(self):
        email = self.cleaned_data.get("email")
        # Проверяем, не занят ли этот email другим пользователем, кроме текущего
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError("Этот email уже используется!")
        return email


# Форма для настройки уведомлений
class NotificationSettingForm(forms.ModelForm):
    class Meta:
        model = NotificationSetting
        fields = ['city', 'frequency']
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите город'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].label = 'Город'
        self.fields['frequency'].label = 'Периодичность уведомлений'

    def clean_city(self):
        city = self.cleaned_data.get('city')
        api_key = settings.WEATHER_API_KEY
        try:
            response = requests.get(
                f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru')
            response.raise_for_status()  # Проверяет ошибки HTTP
            data = response.json()
            if 'cod' in data and data['cod'] != 200:
                raise ValidationError('Город не найден. Пожалуйста, введите правильное название города.')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValidationError('Проверьте правильность ввода города.')  # Пользовательская ошибка для 404
            else:
                raise ValidationError(f'Ошибка при подключении к сервису погоды: {e}')  # Другие HTTP ошибки
        except requests.exceptions.RequestException as e:
            raise ValidationError(f'Ошибка при подключении к сервису погоды: {e}')  # Ошибки подключения

        return city



