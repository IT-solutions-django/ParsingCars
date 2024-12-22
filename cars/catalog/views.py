from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator
from catalog.models import TimeDealCar, TimeDealCarBobaedream, TimeDealCarCharancha, TimeDealCarKcar, TimeDealCarMpark
from .forms import AutoHubFilterForm, BobaedreamFilterForm

DRIVE_MAPPING = {
    'Передний': ['전륜 FF', '전륜'],
    'Задний': ['후륜', '후륜 RR', '후륜 미드쉽'],
    'Полный': ['4WD', 'AWD', '4륜'],
}

TRANSMISSION_MAPPING = {
    'Автомат': ['자동', '오토'],
    'Механика': ['수동'],
    'Полуавтомат': ['세미오토'],
    'Вариатор': ['CVT'],
    'Другое': ['기타']
}


def catalog(request, model_class, title):
    cars = model_class.objects.all()

    if model_class in [TimeDealCarCharancha, TimeDealCar, TimeDealCarMpark]:
        form = AutoHubFilterForm(request.GET)
    elif model_class in [TimeDealCarBobaedream, TimeDealCarKcar]:
        form = BobaedreamFilterForm(request.GET)

    query = Q()
    if form.is_valid():
        transmission = form.cleaned_data.get('transmission')
        if transmission:
            transmission_value = TRANSMISSION_MAPPING.get(transmission, [])
            query &= Q(transmission__in=transmission_value)

        mileage_min = request.GET.get('millage_min')
        mileage_max = request.GET.get('millage_max')

        if mileage_min or mileage_max:
            mileage_query = Q()
            if mileage_min:
                mileage_query &= Q(millage__gte=float(mileage_min))
            if mileage_max:
                mileage_query &= Q(millage__lte=mileage_max)
            query &= mileage_query

        engine_volume_min = request.GET.get('engine_volume_min')
        engine_volume_max = request.GET.get('engine_volume_max')

        if engine_volume_min:
            engine_volume_min = int(engine_volume_min)
        if engine_volume_max:
            engine_volume_max = int(engine_volume_max)

        print(engine_volume_min, engine_volume_max)

        if engine_volume_min or engine_volume_max:
            engine_query = Q()
            if engine_volume_min:
                engine_query &= Q(engine_capacity__gte=engine_volume_min)
            if engine_volume_max:
                engine_query &= Q(engine_capacity__lte=engine_volume_max)
            query &= engine_query

        year_min = request.GET.get('year_min')
        year_max = request.GET.get('year_max')

        if year_min or year_max:
            year_query = Q()
            if year_min:
                year_query &= Q(year__gte=year_min)
            if year_max:
                year_query &= Q(year__lte=year_max)
            query &= year_query

        drive = form.cleaned_data.get('drive')
        if drive:
            drive_values = DRIVE_MAPPING.get(drive, [])
            query &= Q(drive__in=drive_values)

        cars = cars.filter(query)

    paginator = Paginator(cars, 10)

    page_number = request.GET.get('page', 1)
    page_cars = paginator.get_page(page_number)

    if model_class == TimeDealCar:
        add_url_photo = True
    else:
        add_url_photo = False

    return render(request, 'catalog_cars.html',
                  {
                      'page_cars': page_cars,
                      "add_url_photo": add_url_photo,
                      'title': title,
                      'form': form
                  })
