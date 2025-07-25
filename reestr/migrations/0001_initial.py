# Generated by Django 5.2.1 on 2025-05-29 02:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('car', '0004_car_photo1_car_photo2_car_photo3_car_photo4_and_more'),
        ('pod', '0002_podryad_photo1_podryad_photo2_podryad_photo3_and_more'),
        ('vod', '0004_driver_vy_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Marsh',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Маршрут',
                'verbose_name_plural': 'Маршруты',
            },
        ),
        migrations.CreateModel(
            name='Registry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numberPL', models.CharField(blank=True, max_length=100, null=True, verbose_name='Номер путевого листа')),
                ('dataPOPL', models.DateField(blank=True, null=True, verbose_name='Дата погрузки')),
                ('timePOPL', models.TimeField(blank=True, null=True, verbose_name='Время погрузки')),
                ('timeSDPL', models.TimeField(blank=True, null=True, verbose_name='Время сдачи путевого листа')),
                ('dataSDPL', models.DateField(blank=True, null=True, verbose_name='Дата сдачи путевого листа')),
                ('numberTN', models.CharField(blank=True, max_length=100, null=True, verbose_name='Номер ТТН')),
                ('dataPOG', models.DateField(blank=True, null=True, verbose_name='Дата погрузки груза')),
                ('dataVYG', models.DateField(blank=True, null=True, verbose_name='Дата выгрузки груза')),
                ('tonn', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Количество тонн')),
                ('gsm', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='ГСМ')),
                ('gsmVY', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='ГСМ ВЫ')),
                ('gsmVO', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='ГСМ ВО')),
                ('gsmRS', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='ГСМ РС')),
                ('comment', models.TextField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=50, null=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='primary_registries', to='vod.driver')),
                ('driver2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='secondary_registries', to='vod.driver')),
                ('marka', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car.carmarka')),
                ('marsh', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='marsh_reestr', to='reestr.marsh')),
                ('number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carnumber_reestr', to='car.car')),
                ('pod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pod_reestr', to='pod.podryad')),
            ],
            options={
                'verbose_name': 'Реестр',
                'verbose_name_plural': 'Реестры',
            },
        ),
    ]
