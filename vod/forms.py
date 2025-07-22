from django import forms
from .models import Driver

class DriverProfileForm(forms.ModelForm):
    class Meta:
        model = Driver
        # Указываем поля, которые водитель может редактировать
        fields = [
            'full_name', 'birth_date', 'driver_license', 'vy_date', 'snils',
            'issued_by', 'issue_date', 'number', 'series', 'registration',
            'phone_1', 'phone_2', 'phone_3',
            'photo1', 'photo2', 'photo21', 'photo3', 'photo4', 'photo5'
        ]
        
        # Добавляем виджеты для удобного ввода дат
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'vy_date': forms.DateInput(attrs={'type': 'date'}),
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем все поля необязательными, как в модели (blank=True, null=True)
        for field in self.fields:
            self.fields[field].required = False
