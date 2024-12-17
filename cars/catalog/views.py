from django.shortcuts import render
from django.core.paginator import Paginator
from catalog.models import TimeDealCar


def catalog(request, model_class, title):
    cars = model_class.objects.all()
    paginator = Paginator(cars, 10)

    page_number = request.GET.get('page', 1)
    page_cars = paginator.get_page(page_number)

    if model_class == TimeDealCar:
        add_url_photo = True
    else:
        add_url_photo = False

    return render(request, 'catalog_cars.html',
                  {'page_cars': page_cars, "add_url_photo": add_url_photo, 'title': title})
