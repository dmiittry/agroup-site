# Generated by Django 5.2.1 on 2025-05-23 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('car', '0003_carmarka_carmodel_alter_car_marka_alter_car_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Статус согласования')),
                ('full_name', models.CharField(blank=True, help_text='ФИО Полностью', max_length=255, null=True, verbose_name='ФИО')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('driver_license', models.CharField(blank=True, max_length=50, null=True, verbose_name='Номер водительского удостоверения (ВУ)')),
                ('snils', models.CharField(max_length=20, verbose_name='СНИЛС')),
                ('issued_by', models.TextField(blank=True, null=True, verbose_name='Паспорт: Кем выдан')),
                ('issue_date', models.DateField(blank=True, null=True, verbose_name='Дата выдачи')),
                ('number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Номер паспорта')),
                ('series', models.CharField(blank=True, max_length=20, null=True, verbose_name='Серия паспорта')),
                ('registration', models.TextField(blank=True, null=True, verbose_name='Прописка')),
                ('phone_1', models.CharField(blank=True, help_text='89147776655', max_length=20, null=True, verbose_name='Номер телефона 1')),
                ('phone_2', models.CharField(blank=True, help_text='Если есть второй номер', max_length=20, null=True, verbose_name='Номер телефона 2')),
                ('phone_3', models.CharField(blank=True, help_text='Если есть третий номер', max_length=20, null=True, verbose_name='Номер телефона 3')),
                ('cars', models.ManyToManyField(blank=True, null=True, related_name='drivers', to='car.car', verbose_name='Закрепленные ТС')),
            ],
            options={
                'verbose_name': 'Водитель',
                'verbose_name_plural': 'Водители',
            },
        ),
    ]
