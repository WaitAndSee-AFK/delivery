# Generated by Django 5.2 on 2025-04-21 18:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0012_customuser_is_ready'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='claim',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='Претензия'),
        ),
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='Комментарий'),
        ),
        migrations.AddField(
            model_name='order',
            name='courier',
            field=models.ForeignKey(blank=True, limit_choices_to={'role__id': 2}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_courier', to=settings.AUTH_USER_MODEL, verbose_name='Курьер'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('create', 'Создан'), ('courier', 'Доставляет курьер'), ('delivered', 'Вручен'), ('not_delivered', 'Не вручен'), ('cancelled', 'Отменен')], default='courier', max_length=20, verbose_name='Статус заказа'),
        ),
    ]
