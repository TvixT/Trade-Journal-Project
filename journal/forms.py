from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Trade, JournalEntry


class TradeForm(forms.ModelForm):
    """
    Form for creating and updating Trade records.
    """
    
    class Meta:
        model = Trade
        fields = [
            'symbol', 'asset_type', 'position_type', 'entry_price', 'exit_price',
            'position_size', 'entry_date', 'exit_date', 'stop_loss', 'take_profit',
            'commission', 'notes', 'is_open'
        ]
        widgets = {
            'symbol': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., AAPL, BTCUSD',
                'style': 'text-transform: uppercase;'
            }),
            'position_type': forms.Select(attrs={
                'class': 'form-select',
                'help_text': 'Long = Buy expecting price up, Short = Sell expecting price down'
            }),
            'asset_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'entry_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'min': '0.0001'
            }),
            'exit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'min': '0.0001'
            }),
            'position_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'e.g., 10000 (forex), 100 (stocks), 10 (gold oz)'
            }),
            'entry_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'exit_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'stop_loss': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'min': '0.0001'
            }),
            'take_profit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'min': '0.0001'
            }),
            'commission': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.00'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter any additional notes about this trade...'
            }),
            'is_open': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default entry_date to current time
        if not self.instance.pk:
            self.fields['entry_date'].initial = timezone.now()

    def clean_symbol(self):
        """Clean and validate symbol field."""
        symbol = self.cleaned_data.get('symbol')
        if symbol:
            symbol = symbol.upper().strip()
            if len(symbol) < 1 or len(symbol) > 10:
                raise ValidationError("Symbol must be between 1 and 10 characters.")
        return symbol

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        entry_date = cleaned_data.get('entry_date')
        exit_date = cleaned_data.get('exit_date')
        entry_price = cleaned_data.get('entry_price')
        exit_price = cleaned_data.get('exit_price')
        is_open = cleaned_data.get('is_open')

        # Validate date logic
        if entry_date and exit_date:
            if exit_date <= entry_date:
                raise ValidationError("Exit date must be after entry date.")

        # Validate open position logic
        if not is_open and not exit_price:
            raise ValidationError("Exit price is required for closed positions.")
        
        if not is_open and not exit_date:
            cleaned_data['exit_date'] = timezone.now()

        # Validate price logic
        if entry_price and entry_price <= 0:
            raise ValidationError("Entry price must be positive.")
        
        if exit_price and exit_price <= 0:
            raise ValidationError("Exit price must be positive.")

        return cleaned_data


class JournalEntryForm(forms.ModelForm):
    """
    Form for creating and updating JournalEntry records.
    """
    
    class Meta:
        model = JournalEntry
        fields = [
            'trade', 'title', 'content', 'entry_date', 'mood',
            'market_conditions', 'strategy_used', 'lessons_learned', 'tags', 'rating'
        ]
        widgets = {
            'trade': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a descriptive title for your journal entry...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Write your detailed thoughts, analysis, and reflections...'
            }),
            'entry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'mood': forms.Select(attrs={'class': 'form-select'}),
            'market_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the market conditions during this trade...'
            }),
            'strategy_used': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Breakout, Mean Reversion, Momentum...'
            }),
            'lessons_learned': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What did you learn from this experience?'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., swing trade, earnings play, technical analysis (comma-separated)'
            }),
            'rating': forms.Select(
                choices=[(None, 'Select rating...')] + [(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-select'}
            )
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter trades to only show user's trades
        self.fields['trade'].queryset = Trade.objects.filter(user=user)
        self.fields['trade'].empty_label = "No specific trade (general entry)"
        
        # Set default entry_date to today
        if not self.instance.pk:
            self.fields['entry_date'].initial = timezone.now().date()

    def clean_title(self):
        """Clean and validate title field."""
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 5:
            raise ValidationError("Title must be at least 5 characters long.")
        return title.strip() if title else title

    def clean_content(self):
        """Clean and validate content field."""
        content = self.cleaned_data.get('content')
        if content and len(content.strip()) < 10:
            raise ValidationError("Content must be at least 10 characters long.")
        return content.strip() if content else content

    def clean_tags(self):
        """Clean and validate tags field."""
        tags = self.cleaned_data.get('tags')
        if tags:
            # Clean up tags: remove extra spaces, convert to lowercase
            tag_list = [tag.strip().lower() for tag in tags.split(',') if tag.strip()]
            return ', '.join(tag_list)
        return tags

    def clean_entry_date(self):
        """Validate entry date."""
        entry_date = self.cleaned_data.get('entry_date')
        if entry_date and entry_date > timezone.now().date():
            raise ValidationError("Entry date cannot be in the future.")
        return entry_date


class TradeFilterForm(forms.Form):
    """
    Form for filtering trades in the list view.
    """
    symbol = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by symbol...'
        })
    )
    position_type = forms.ChoiceField(
        choices=[('', 'All Positions')] + Trade.POSITION_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('open', 'Open'),
            ('win', 'Win'),
            ('loss', 'Loss'),
            ('breakeven', 'Breakeven')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class JournalFilterForm(forms.Form):
    """
    Form for filtering journal entries in the list view.
    """
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search in title, content, or tags...'
        })
    )
    mood = forms.ChoiceField(
        choices=[('', 'All Moods')] + JournalEntry.MOOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    rating = forms.ChoiceField(
        choices=[('', 'All Ratings')] + [(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )