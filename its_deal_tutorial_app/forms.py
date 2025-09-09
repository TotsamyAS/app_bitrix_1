from django import forms
from django.core.validators import MinValueValidator
from datetime import date

class DealForm(forms.Form):
    auth_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    refresh_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    domain = forms.CharField(widget=forms.HiddenInput(), required=False)
    title = forms.CharField(
        label='Название сделки',
        max_length=100,
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    opportunity = forms.DecimalField(
        label = 'Бюджет',
        max_digits = 10,
        decimal_places = 2,
        widget=forms.NumberInput(attrs={'class':'form-control'})
    )
    start_date = forms.DateField(
        label='Дата начала*',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': 'required'
        }),
        initial=date.today
    )

    end_date = forms.DateField(
        label='Дата завершения*',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': 'required'
        }),
        initial=date.today
    )
    # Адресные поля
    delivery_address = forms.CharField(
        label='Адрес доставки*',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("Дата начала не может быть позже даты завершения!")

        return cleaned_data