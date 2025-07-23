from django import forms
from .models import Driver
from django.contrib.auth.models import User

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

class DriverSignupForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            "full_name", "birth_date", "driver_license", "vy_date", "snils",
            "issued_by", "issue_date", "number", "series", "registration",
            "phone_1", "phone_2", "phone_3",
            "photo1", "photo2", "photo21", "photo3", "photo4", "photo5",
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_approved = False  # по умолчанию не одобрен
        if commit:
            instance.save()
        return instance
    
class UserChangeForm(forms.ModelForm):
    username = forms.CharField(label="Логин (номер телефона)", max_length=150)
    password1 = forms.CharField(label="Новый пароль", required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повторите новый пароль", required=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Пароли не совпадают")
            if len(password1.strip()) < 6:
                raise forms.ValidationError("Пароль должен быть не короче 6 символов.")
        # Проверка уникальности username
        username = cleaned_data.get('username')
        if username and User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Пользователь с таким логином уже существует.")
        return cleaned_data