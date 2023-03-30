from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    REQUIRED_FILES = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
