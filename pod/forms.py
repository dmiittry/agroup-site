from django import forms
from .models import Podryad, PodryadPhoto
from django.contrib.auth.models import User
from datetime import datetime 

class PodryadPhotoEditForm(forms.ModelForm):
    class Meta:
        model = PodryadPhoto
        fields = ['description']
        
class PodryadPhotoForm(forms.ModelForm):
    class Meta:
        model = PodryadPhoto
        fields = ['image', 'description']
        
class PodryadProfileForm(forms.ModelForm):
    class Meta:
        model = Podryad
        fields = [
            'org_name', 'full_name', 'birth_date', 'snils',
            'issued_by', 'issue_date', 'number', 'series', 'registration',
            'bank', 'inn', 'kpp', 'num_chet', 'num_bik', 'num_corch',
            'email', 'phone_1', 'phone_2', 'phone_3',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
        }

    # Все поля не обязательны для ввода, если это делаете по аналогии с моделью
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['class'] = 'form-control'
            else:
                # Добавляем специальный класс для полей с датой
                if field_name in ['birth_date', 'issue_date']:
                    field.widget.attrs['class'] = 'form-control form-control-lg datepicker-input'
                    field.widget.attrs['autocomplete'] = 'off' # Отключаем автозаполнение
                else:
                    field.widget.attrs['class'] = 'form-control form-control-lg'

class PodryadSignupForm(forms.ModelForm):
    class Meta:
        model = Podryad
        fields = [
            "org_name", "full_name", "birth_date", "snils",
            "issued_by", "issue_date", "number", "series", "registration",
            "bank", "inn", "kpp", "num_chet", "num_bik", "num_corch",
            "email", "phone_1", "phone_2", "phone_3",
        ]
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
        if commit:
            instance.save()
        return instance
    
class ContractorUserChangeForm(forms.ModelForm):
    username = forms.CharField(label="Логин (номер телефона)", max_length=150)
    password1 = forms.CharField(
        label="Новый пароль", required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Повторите новый пароль", required=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Применяем классы Bootstrap ко всем полям формы
        for field_name, field in self.fields.items():
            # Для полей с файлами (ImageField) используется свой класс
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['class'] = 'form-control'
            # Для полей с датой класс уже задан в widgets, их пропускаем
            elif not isinstance(field.widget, forms.DateInput):
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
        # Проверка уникальности username
        username = cleaned_data.get('username')
        if username and User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Пользователь с таким логином уже существует.")
        return cleaned_data
    
