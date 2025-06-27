from django import forms

class PositionSizeCalculatorForm(forms.Form):
    account_balance = forms.DecimalField(
        label="Account Balance",
        min_value=0.01,
        decimal_places=2,
        max_digits=12,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your account balance',
            'step': '0.01',
        })
    )
    risk_percent = forms.DecimalField(
        label="Risk % per Trade",
        min_value=0.01,
        max_value=100,
        decimal_places=2,
        max_digits=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Risk percent (e.g. 1)',
            'step': '0.01',
        })
    )
    entry_price = forms.DecimalField(
        label="Entry Price",
        min_value=0.0001,
        decimal_places=4,
        max_digits=12,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entry price',
            'step': '0.0001',
        })
    )
    stop_loss_price = forms.DecimalField(
        label="Stop Loss Price",
        min_value=0.0001,
        decimal_places=4,
        max_digits=12,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Stop loss price',
            'step': '0.0001',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        entry = cleaned_data.get('entry_price')
        stop = cleaned_data.get('stop_loss_price')
        if entry and stop and entry == stop:
            self.add_error('stop_loss_price', 'Entry and stop loss price must differ.')
        return cleaned_data
