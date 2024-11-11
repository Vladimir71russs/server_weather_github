import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import UserLoginForm
from .models import NotificationSetting
from .forms import UserRegistrationForm, EditProfileForm, NotificationSettingForm
from .utils import email_verification_token


# Представление для регистрации
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Делаем пользователя неактивным, пока он не подтвердит email
            user.save()
            # Создаем ссылку подтверждения
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = email_verification_token.make_token(user)
            verification_url = request.build_absolute_uri(
                reverse('email_verification', kwargs={'uidb64': uid, 'token': token})
            )
            # Отправка письма
            send_mail(
                'Подтверждение электронной почты',
                f'Пожалуйста, подтвердите ваш email, перейдя по ссылке: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, "Вам на почту отправлено письмо для подтверждения регистрации.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})



def email_verification_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Вы успешно зарегистрировались!")
        return redirect('profile')
    else:
        messages.error(request, "Ссылка для подтверждения недействительна.")
        return redirect('login')


# Представление для авторизации
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Вы успешно вошли в систему!")
            return redirect('profile')
        else:
            messages.error(request, "Неверные данные для входа")
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


# Представление для выхода
def logout_view(request):
    logout(request)
    return redirect('base')


# Представление для профиля
@login_required  # Доступ к этой функции имеют только авторизованные пользователи
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})


# Представление для редактирования профиля
@login_required  # Доступ к этой функции имеют только авторизованные пользователи
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваши данные были успешно обновлены!")  # Сообщение об успехе
            return redirect('profile')
        else:
            messages.error(request, "Произошла ошибка при обновлении профиля. Проверьте введённые данные.")  # Сообщение об ошибке
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'users/edit_profile.html', {'form': form})


# Предстваление для удаления профиля
@login_required
def delete_profile_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)  # Сначала выходим из системы
        user.delete()  # Удаляем профиль
        messages.success(request, "Ваш профиль был успешно удален.")
        return redirect('base')  # Перенаправляем на главную страницу
    return redirect('profile')


# Представление для списка уведомлений
@login_required
def notification_list_view(request):
    notifications = NotificationSetting.objects.filter(user=request.user)
    return render(request, 'users/notification_list.html', {'notifications': notifications})


# Представление для добавления уведомлений
@login_required
def add_notification_view(request):
    if request.method == 'POST':
        form = NotificationSettingForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data.get('city')
            api_key = settings.WEATHER_API_KEY
            # Пример проверки города через API
            response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru')
            if response.status_code == 200:
                notification = form.save(commit=False)
                notification.user = request.user
                notification.save()
                messages.success(request, 'Уведомление успешно добавлено.')
                return redirect('notification_list')

        else:
            messages.error(request, 'Город не найден. Пожалуйста, введите правильное название города.')
    else:
        form = NotificationSettingForm()

    return render(request, 'users/add_notification.html', {'form': form})


# Представление для удаления уведомлений
@login_required
def delete_notification_view(request, notification_id):
    notification = get_object_or_404(NotificationSetting, id=notification_id, user=request.user)
    notification.delete()
    messages.success(request, 'Уведомление удалено.')
    return redirect('notification_list')