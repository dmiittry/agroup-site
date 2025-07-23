from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Podryad
import random
import string

@receiver(post_save, sender=Podryad)
def create_podryad_user(sender, instance, created, **kwargs):
    """
    Автоматически создает пользователя для подрядчика при создании нового объекта Podryad,
    если пользователь еще не привязан.
    """
    def make_random_password(length=10):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))

    if created and not instance.user:
        # Логин — номер телефона, если есть
        base_username = (instance.phone_1 or '').strip()
        if not base_username:
            # fallback если телефон не указан
            base_username = 'pod' + ''.join(random.choices(string.digits, k=8))

        username = base_username
        suffix = 0
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base_username}_{suffix}"

        password = make_random_password()
        user = User.objects.create_user(username=username, password=password)
        instance.user = user
        instance.save()
        print(f"Создан пользователь для подрядчика '{instance.org_name}'")
        print(f"Логин (номер телефона): {username}")
        print(f"Пароль: {password}")
