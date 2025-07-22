from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Podryad
import random
import string

@receiver(post_save, sender=Podryad)
def create_podryad_user(sender, instance, created, **kwargs):
    """
    Автоматически создает пользователя при создании нового водителя,
    если пользователь еще не привязан.
    """
    if created and not instance.user:
        # Генерируем уникальное имя пользователя (например, из ФИО и случайных цифр)
        base_username = ''.join(filter(str.isalnum, instance.full_name)).lower()[:20]
        unique_suffix = ''.join(random.choices(string.digits, k=4))
        username = f"{base_username}_{unique_suffix}"
        
        # Проверяем, что такое имя пользователя еще не занято
        while User.objects.filter(username=username).exists():
            unique_suffix = ''.join(random.choices(string.digits, k=4))
            username = f"{base_username}_{unique_suffix}"

        # Создаем пользователя с временным паролем (пользователь должен будет его сменить)
        password = User.objects.make_random_password()
        user = User.objects.create_user(username=username, password=password)
        
        # Привязываем созданного пользователя к водителю
        instance.user = user
        instance.save()

        # Выводим в консоль данные для входа (в реальном проекте их нужно отправлять на email)
        print(f"Создан пользователь для водителя '{instance.full_name}'.")
        print(f"Логин: {username}")
        print(f"Пароль: {password}")

