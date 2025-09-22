# car/forms.py
from django import forms
from .models import Car

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['number', 'marka', 'model']  # только существующие поля
