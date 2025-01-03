from django import forms


class AutoHubFilterForm(forms.Form):
    TRANSMISSION_CHOICES = [
        ('', ''),
        ('Автомат', 'Автомат'),
        ('Механика', 'Механика'),
        ('Полуавтомат', 'Полуавтомат'),
        ('Вариатор', 'Вариатор'),
        ('Другое', 'Другое'),
    ]
    transmission = forms.ChoiceField(
        choices=TRANSMISSION_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    millage_min = forms.IntegerField(
        min_value=10000,
        max_value=200000,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пробег от, km',
            'step': '10000',
            'onkeypress': 'limitCharacters(this, 6, event)',
        })
    )
    millage_max = forms.IntegerField(
        min_value=10000,
        max_value=200000,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'до',
            'step': '10000',
            'onkeypress': 'limitCharacters(this, 6, event)',
        })
    )

    engine_volume_min = forms.IntegerField(
        min_value=0,
        max_value=10000,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Объем от, cc',
            'step': '100'
        })
    )
    engine_volume_max = forms.IntegerField(
        min_value=0,
        max_value=10000,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'до',
            'step': '100'
        })
    )


class BobaedreamFilterForm(forms.Form):
    TRANSMISSION_CHOICES = [
        ('', ''),
        ('Автомат', 'Автомат'),
        ('Механика', 'Механика'),
    ]

    DRIVE_CHOICES = [
        ('', ''),
        ('Передний', 'Передний привод'),
        ('Задний', 'Задний привод'),
        ('Полный', 'Полный привод'),
    ]

    transmission = forms.ChoiceField(
        choices=TRANSMISSION_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    drive = forms.ChoiceField(
        choices=DRIVE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    millage_min = forms.IntegerField(
        min_value=10000,
        max_value=200000,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пробег от, km',
            'step': '10000',
            'onkeypress': 'limitCharacters(this, 6, event)',
        })
    )
    millage_max = forms.IntegerField(
        min_value=10000,
        max_value=200000,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'до',
            'step': '10000',
            'onkeypress': 'limitCharacters(this, 6, event)',
        })
    )
