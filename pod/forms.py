from django import forms
from .models import Podryad
from django.contrib.auth.models import User

class PodryadProfileForm(forms.ModelForm):
    class Meta:
        model = Podryad
        fields = [
            'org_name', 'full_name', 'birth_date', 'snils',
            'issued_by', 'issue_date', 'number', 'series', 'registration',
            'bank', 'inn', 'kpp', 'num_chet', 'num_bik', 'num_corch',
            'email', 'phone_1', 'phone_2', 'phone_3',
            'photo1', 'photo2', 'photo3', 'photo4', 'photo5',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
        }

    # Все поля не обязательны для ввода, если это делаете по аналогии с моделью
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.required = False

class PodryadSignupForm(forms.ModelForm):
    class Meta:
        model = Podryad
        fields = [
            "org_name", "full_name", "birth_date", "snils",
            "issued_by", "issue_date", "number", "series", "registration",
            "bank", "inn", "kpp", "num_chet", "num_bik", "num_corch",
            "email", "phone_1", "phone_2", "phone_3",
            "photo1", "photo2", "photo3", "photo4", "photo5",
        ]

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
    
