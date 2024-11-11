from django.urls import path

from users.views import register_view, login_view, profile_view, edit_profile_view, logout_view, delete_profile_view, \
    notification_list_view, delete_notification_view, add_notification_view, email_verification_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),
    path('profile/delete/', delete_profile_view, name='delete_profile'),
    path('notifications/', notification_list_view, name='notification_list'),
    path('notifications/add/', add_notification_view, name='add_notification'),
    path('delete/<int:notification_id>/', delete_notification_view, name='delete_notification'),
    path('email-verification/<uidb64>/<token>/', email_verification_view, name='email_verification'),

]