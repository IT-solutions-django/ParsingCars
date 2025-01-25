from django import forms
from .models import TimeDealCarEncar


class AutoHubFilterForm(forms.Form):
    TRANSMISSION_CHOICES = [
        ('', ''),
        ('Автомат', 'Автомат'),
        ('Механика', 'Механика'),
        ('Полуавтомат', 'Полуавтомат'),
        ('Вариатор', 'Вариатор'),
        ('Другое', 'Другое'),
    ]
    MILLAGE_CHOICES = [('', '')] + [
        (i, i)
        for i in range(10000, 200000 + 1, 10000)
    ]

    YEAR_CHOICES = [('', '')] + [
        (i, i)
        for i in range(2008, 2026)
    ]

    ENGINE_VOLUME_CHOICES = [('', '')] + [
        (i, i / 1000)
        for i in range(0, 10000 + 1, 100)
    ]

    SORT_CHOICES = [
        ('', ''),
        ('new', 'Сначала новые'),
        ('old', 'Сначала старые'),
        ('low_millage', 'Сначала с низким пробегом'),
        ('high_millage', 'Сначала с высоким пробегом')
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
    millage_min = forms.ChoiceField(
        choices=MILLAGE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )
    millage_max = forms.ChoiceField(
        choices=MILLAGE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )
    engine_volume_min = forms.ChoiceField(
        choices=ENGINE_VOLUME_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )
    engine_volume_max = forms.ChoiceField(
        choices=ENGINE_VOLUME_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    year_min = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    year_max = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
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
        ('Автомат', 'Автомат'),
        ('Механика', 'Механика'),
    ]

    DRIVE_CHOICES = [
        ('', ''),
        ('Передний', 'Передний привод'),
        ('Задний', 'Задний привод'),
        ('Полный', 'Полный привод'),
    ]

    MILLAGE_CHOICES = [('', '')] + [
        (i, i)
        for i in range(10000, 200000 + 1, 10000)
    ]

    YEAR_CHOICES = [('', '')] + [
        (i, i)
        for i in range(2008, 2026)
    ]

    ENGINE_VOLUME_CHOICES = [('', '')] + [
        (i, i / 1000)
        for i in range(0, 10000 + 1, 100)
    ]

    SORT_CHOICES = [
        ('', ''),
        ('new', 'Сначала новые'),
        ('old', 'Сначала старые'),
        ('low_millage', 'Сначала с низким пробегом'),
        ('high_millage', 'Сначала с высоким пробегом')
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

    millage_min = forms.ChoiceField(
        choices=MILLAGE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )
    millage_max = forms.ChoiceField(
        choices=MILLAGE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )
    engine_volume_min = forms.ChoiceField(
        choices=ENGINE_VOLUME_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )
    engine_volume_max = forms.ChoiceField(
        choices=ENGINE_VOLUME_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    year_min = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    year_max = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )


class EncarFilterForm(forms.Form):
    TRANSMISSION_CHOICES = [
        ('', ''),
        ('MT', 'Механика'),
        ('AT', 'Автомат'),
    ]

    FUEL_TYPE_CHOICES = [
        ('', ''),
        ('D', 'Дизель'),
        ('E', 'Электро'),
        ('G', 'Бензин'),
        ('H', 'Гибрид'),
        ('L', 'Сниженный газ')
    ]

    MILLAGE_CHOICES = [('', '')] + [
        (i, i)
        for i in range(10000, 200000 + 1, 10000)
    ]

    YEAR_CHOICES = [('', '')] + [
        (i, i)
        for i in range(2008, 2026)
    ]

    ENGINE_VOLUME_CHOICES = [('', '')] + [
        (i, i / 1000)
        for i in range(0, 10000 + 1, 100)
    ]

    COLOR_CHOICES = [('', '')] + [
        (item['color'], item['color'])
        for item in TimeDealCarEncar.objects.values('color').filter(color__isnull=False).distinct()
    ]

    MARKA_CHOICES = [('', '')] + [
        (item['marka_name'], item['marka_name'])
        for item in TimeDealCarEncar.objects.values('marka_name').filter(marka_name__isnull=False).distinct()
    ]

    SORT_CHOICES = [
        ('', ''),
        ('new', 'Сначала новые'),
        ('old', 'Сначала старые'),
        ('low_millage', 'Сначала с низким пробегом'),
        ('high_millage', 'Сначала с высоким пробегом')
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
    millage_min = forms.ChoiceField(
        choices=MILLAGE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )
    millage_max = forms.ChoiceField(
        choices=MILLAGE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )
    engine_volume_min = forms.ChoiceField(
        choices=ENGINE_VOLUME_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )
    engine_volume_max = forms.ChoiceField(
        choices=ENGINE_VOLUME_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    fuel_type = forms.ChoiceField(
        choices=FUEL_TYPE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    year_min = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    year_max = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    color = forms.ChoiceField(
        choices=COLOR_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    brand = forms.ChoiceField(
        choices=MARKA_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )
