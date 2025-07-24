from django import forms
from .models import Driver
from django.contrib.auth.models import User
from datetime import datetime 

class DriverProfileForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            'full_name', 'birth_date', 'driver_license', 'vy_date', 'snils',
            'issued_by', 'issue_date', 'number', 'series', 'registration',
            'phone_1', 'phone_2', 'phone_3',
            'photo1', 'photo2', 'photo21', 'photo3', 'photo4', 'photo5'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'vy_date': forms.DateInput(attrs={'type': 'date'}),
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control form-control-lg'
        
        for field in self.fields.values():
            field.required = False


class DriverSignupForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            "full_name", "birth_date", "driver_license", "vy_date", "snils",
            "issued_by", "issue_date", "number", "series", "registration",
            "phone_1", "phone_2", "phone_3",
            "photo1", "photo2", "photo21", "photo3", "photo4", "photo5",
        ]
        # ДОБАВЛЕНЫ ВИДЖЕТЫ ДЛЯ ПОЛЕЙ С ДАТОЙ
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'vy_date': forms.DateInput(attrs={'type': 'date'}),
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Применяем классы Bootstrap ко всем полям
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['class'] = 'form-control'
            else:
                # Добавляем специальный класс для полей с датой
                if field_name in ['birth_date', 'vy_date', 'issue_date']:
                    field.widget.attrs['class'] = 'form-control form-control-lg datepicker-input'
                    field.widget.attrs['placeholder'] = 'Выберите дату...'
                    field.widget.attrs['autocomplete'] = 'off'
                else:
                    field.widget.attrs['class'] = 'form-control form-control-lg'

    # Методы для правильной обработки даты из календаря
    def clean_birth_date(self):
        date_str = self.cleaned_data.get('birth_date')
        if date_str:
            try: return datetime.strptime(date_str, '%d.%m.%Y').date()
            except (ValueError, TypeError): raise forms.ValidationError("Выберите корректную дату.")
        return date_str

    def clean_vy_date(self):
        date_str = self.cleaned_data.get('vy_date')
        if date_str:
            try: return datetime.strptime(date_str, '%d.%m.%Y').date()
            except (ValueError, TypeError): raise forms.ValidationError("Выберите корректную дату.")
        return date_str

    def clean_issue_date(self):
        date_str = self.cleaned_data.get('issue_date')
        if date_str:
            try: return datetime.strptime(date_str, '%d.%m.%Y').date()
            except (ValueError, TypeError): raise forms.ValidationError("Выберите корректную дату.")
        return date_str

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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-control-lg'
            
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Пароли не совпадают")
            if len(password1.strip()) < 6:
                raise forms.ValidationError("Пароль должен быть не короче 6 символов.")
        username = cleaned_data.get('username')
        if username and User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Пользователь с таким логином уже существует.")
        return cleaned_data
