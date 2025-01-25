from django.urls import path
from catalog.views import catalog, catalog_encar, api_cars_brand, car
from catalog.models import TimeDealCar, TimeDealCarBobaedream, TimeDealCarCharancha, TimeDealCarKcar, TimeDealCarMpark, \
    TimeDealCarEncar

app_name = 'catalog'

urlpatterns = [
    path('autohub/', catalog, {'model_class': TimeDealCar, 'title': 'AutoHub'}, name='autohub'),
    path('bobaedream/', catalog, {'model_class': TimeDealCarBobaedream, 'title': 'Bobaedream'}, name='bobaedream'),
    path('charancha/', catalog, {'model_class': TimeDealCarCharancha, 'title': 'Charancha'}, name='charancha'),
    path('kcar/', catalog, {'model_class': TimeDealCarKcar, 'title': 'Kcar'}, name='kcar'),
    path('mpark/', catalog, {'model_class': TimeDealCarMpark, 'title': 'Mpark'}, name='mpark'),
    path('encar/', catalog_encar, {'model_class': TimeDealCarEncar, 'title': 'Encar'}, name='encar'),
    path('api/cars/brand/', api_cars_brand, name='api-cars-brand'),
    path('car/<str:car_id>/', car, name='car')
]
