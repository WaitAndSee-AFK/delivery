from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название роли")

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True)
    first_name = models.CharField(max_length=30, verbose_name="Имя", blank=False)
    last_name = models.CharField(max_length=30, verbose_name="Фамилия", blank=False)

    # Пока не связываем с Role (добавим позже)
    # role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"