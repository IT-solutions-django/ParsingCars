from django import forms


class AutoHubFilterForm(forms.Form):
    TRANSMISSION_CHOICES = [
        ('', ''),
        ('자동', 'Автомат'),
        ('수동', 'Механика'),
        ('세미오토', 'Полуавтомат'),
        ('CVT', 'Вариатор'),
        ('기타', 'Другое'),
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


class BobaedreamFilterForm(forms.Form):
    TRANSMISSION_CHOICES = [
        ('', ''),
        ('자동', 'Автомат'),
        ('수동', 'Механика'),
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
