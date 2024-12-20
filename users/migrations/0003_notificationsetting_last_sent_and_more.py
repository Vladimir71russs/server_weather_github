# Generated by Django 5.1.2 on 2024-11-09 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_notificationsetting'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationsetting',
            name='last_sent',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='notificationsetting',
            name='frequency',
            field=models.CharField(choices=[('hourly', 'Каждый час'), ('daily_9am', 'Ежедневно в 9:00')], max_length=20),
        ),
    ]
