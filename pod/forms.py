from django import forms
from .models import Podryad

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
