# Generated by Django 5.2.1 on 2025-05-22 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Podryad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('org_name', models.CharField(help_text='Например: ООО Компания или ИП Иванов Иван Иванович (ФИО Полностью)', max_length=255, verbose_name='Название организации')),
                ('full_name', models.CharField(blank=True, help_text='ФИО директора полностью', max_length=255, null=True, verbose_name='ФИО')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('snils', models.CharField(blank=True, max_length=20, null=True, verbose_name='СНИЛС')),
                ('issued_by', models.TextField(blank=True, null=True, verbose_name='Паспорт: Кем выдан')),
                ('issue_date', models.DateField(blank=True, null=True, verbose_name='Дата выдачи')),
                ('number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Номер паспорта')),
                ('series', models.CharField(blank=True, max_length=20, null=True, verbose_name='Серия паспорта')),
                ('registration', models.TextField(blank=True, null=True, verbose_name='Прописка')),
                ('bank', models.CharField(blank=True, help_text='Реквизиты организации', max_length=30, null=True, verbose_name='Банк')),
                ('inn', models.CharField(blank=True, max_length=20, null=True, verbose_name='ИНН')),
                ('kpp', models.CharField(blank=True, max_length=20, null=True, verbose_name='КПП')),
                ('num_chet', models.CharField(blank=True, max_length=30, null=True, verbose_name='Номер р/счета')),
                ('num_bik', models.CharField(blank=True, max_length=30, null=True, verbose_name='Номер БИК')),
                ('num_corch', models.CharField(blank=True, max_length=30, null=True, verbose_name='Номер корр/сч')),
                ('email', models.CharField(blank=True, max_length=30, null=True, verbose_name='Эл. почта')),
                ('phone_1', models.CharField(blank=True, help_text='89147776655', max_length=20, null=True, verbose_name='Номер телефона 1')),
                ('phone_2', models.CharField(blank=True, help_text='Если есть второй номер', max_length=20, null=True, verbose_name='Номер телефона 2')),
                ('phone_3', models.CharField(blank=True, help_text='Можно номер бухгалтера', max_length=20, null=True, verbose_name='Номер телефона 3')),
            ],
            options={
                'verbose_name': 'Подрядчик',
                'verbose_name_plural': 'Подрядчики',
            },
        ),
    ]
