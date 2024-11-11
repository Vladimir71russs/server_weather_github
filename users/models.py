from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'

# Сигнал для автоматического создания профиля
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class NotificationSetting(models.Model):
    CITY_CHOICES = [
        ('every_minute', 'Каждую минуту'),
        ('hourly', 'Каждый час'),
        ('every_3_hours', 'Каждые 3 часа'),
        ('every_12_hours', 'Каждые 12 часов'),
        ('daily_9am', 'Ежедневно в 9:00'),
        ('weekly', 'Еженедельно'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    city = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=CITY_CHOICES)
    last_sent = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Уведомление для {self.user.username} - {self.city} ({self.get_frequency_display()})'
