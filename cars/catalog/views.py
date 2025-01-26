from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator
from catalog.models import TimeDealCar, TimeDealCarBobaedream, TimeDealCarCharancha, TimeDealCarKcar, TimeDealCarMpark, \
    TimeDealCarEncar
from .forms import AutoHubFilterForm, BobaedreamFilterForm, EncarFilterForm
from django.http import JsonResponse

DRIVE_MAPPING = {
    'Передний': ['전륜 FF', '전륜', 'FF'],
    'Задний': ['후륜', '후륜 RR', '후륜 미드쉽'],
    'Полный': ['4WD', 'AWD', '4륜', 'FULLTIME4WD', 'FF,FULLTIME4WD'],
}

TRANSMISSION_MAPPING = {
    'Автомат': ['자동', '오토'],
    'Механика': ['수동'],
    'Полуавтомат': ['세미오토'],
    'Вариатор': ['CVT'],
    'Другое': ['기타']
}


def catalog(request, model_class, title):
    cars = model_class.objects.filter(main_image__isnull=False).all()

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

        sort = form.cleaned_data.get('sort')
        if sort:
            if sort == 'new':
                cars = cars.order_by('-year')
            elif sort == 'old':
                cars = cars.order_by('year')
            elif sort == 'low_millage':
                cars = cars.order_by('millage')
            elif sort == 'high_millage':
                cars = cars.order_by('-millage')

    total_cars = cars.count()

    paginator = Paginator(cars, 12)

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
                      'form': form,
                      'total_cars': total_cars
                  })


def catalog_encar(request, model_class, title):
    cars = model_class.objects.all()

    form = EncarFilterForm(request.GET)

    query = Q()
    if form.is_valid():
        brand = form.cleaned_data.get('brand')
        if brand:
            query &= Q(marka_name=brand)

        model = request.GET.get('model')
        if model:
            query &= Q(model_name=model)

        color = form.cleaned_data.get('color')
        if color:
            query &= Q(color=color)

        transmission = form.cleaned_data.get('transmission')
        if transmission:
            if transmission == 'MT':
                query &= Q(kpp=transmission)
            else:
                query &= (Q(kpp=transmission) | Q(kpp=''))

        mileage_min = request.GET.get('millage_min')
        mileage_max = request.GET.get('millage_max')

        if mileage_min or mileage_max:
            mileage_query = Q()
            if mileage_min:
                mileage_query &= Q(mileage__gte=mileage_min)
            if mileage_max:
                mileage_query &= Q(mileage__lte=mileage_max)
            query &= mileage_query

        engine_volume_min = request.GET.get('engine_volume_min')
        engine_volume_max = request.GET.get('engine_volume_max')

        if engine_volume_min or engine_volume_max:
            engine_query = Q()
            if engine_volume_min:
                engine_query &= Q(eng_v__gte=engine_volume_min)
            if engine_volume_max:
                engine_query &= Q(eng_v__lte=engine_volume_max)
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

        fuel_type = form.cleaned_data.get('fuel_type')
        if fuel_type:
            query &= Q(time=fuel_type)

        cars = cars.filter(query)

        sort = form.cleaned_data.get('sort')
        if sort:
            if sort == 'new':
                cars = cars.order_by('-year')
            elif sort == 'old':
                cars = cars.order_by('year')
            elif sort == 'low_millage':
                cars = cars.order_by('mileage')
            elif sort == 'high_millage':
                cars = cars.order_by('-mileage')

    total_cars = cars.count()

    paginator = Paginator(cars, 12)

    page_number = request.GET.get('page', 1)
    page_cars = paginator.get_page(page_number)

    if model_class == TimeDealCar:
        add_url_photo = True
    else:
        add_url_photo = False
    return render(request, 'catalog_encar.html',
                  {
                      'page_cars': page_cars,
                      "add_url_photo": add_url_photo,
                      'title': title,
                      'form': form,
                      'total_cars': total_cars,
                  }
                  )


def api_cars_brand(request):
    brand = request.GET.get('brand')
    models_dict = TimeDealCarEncar.objects.filter(marka_name=brand).values('model_name').distinct()

    models = [model['model_name'] for model in models_dict]

    return JsonResponse(models, safe=False)


def car(request, car_id):
    car_search = TimeDealCarEncar.objects.get(id=car_id)
    return render(request, 'car.html', {'car': car_search})
