from django.db import models


class TimeDealCar(models.Model):
    id_car = models.CharField(max_length=255, unique=True)
    url_car = models.CharField(max_length=255)
    car_mark = models.CharField(max_length=255, null=True, blank=True)
    car_model = models.CharField(max_length=255, null=True, blank=True)
    price = models.CharField(max_length=255, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    millage = models.IntegerField(null=True, blank=True)
    images = models.TextField(null=True, blank=True)
    main_image = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=255, null=True, blank=True)
    transmission = models.CharField(max_length=255, null=True, blank=True)
    engine_capacity = models.IntegerField(null=True, blank=True)
    car_fuel = models.CharField(max_length=255, null=True, blank=True)
    car_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'site_autohub_cars'


class TimeDealCarBobaedream(models.Model):
    id_car = models.CharField(max_length=255)
    url_car = models.URLField()
    car_mark = models.CharField(max_length=255)
    car_model = models.CharField(max_length=255)
    drive = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    year = models.IntegerField()
    millage = models.IntegerField()
    images = models.TextField()
    main_image = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    transmission = models.CharField(max_length=255)
    engine_capacity = models.IntegerField()
    car_fuel = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'site_bobaedream_cars'


class TimeDealCarCharancha(models.Model):
    id_car = models.CharField(max_length=255)
    url_car = models.URLField(max_length=255)
    car_mark = models.CharField(max_length=255)
    car_model = models.CharField(max_length=255)
    car_complectation = models.CharField(max_length=255)
    car_type = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    year = models.IntegerField()
    millage = models.IntegerField()
    images = models.TextField()
    main_image = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    transmission = models.CharField(max_length=255)
    engine_capacity = models.IntegerField()
    car_fuel = models.CharField(max_length=255)
    car_description = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'site_charancha_cars'


class TimeDealCarKcar(models.Model):
    id_car = models.CharField(max_length=255)
    url_car = models.URLField(max_length=255)
    car_model = models.CharField(max_length=255)
    car_mark = models.CharField(max_length=255)
    price = models.IntegerField()
    main_image = models.CharField(max_length=255)
    images = models.TextField()
    year = models.IntegerField()
    millage = models.IntegerField()
    drive = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    car_fuel = models.CharField(max_length=255)
    transmission = models.CharField(max_length=255)
    car_noAccident = models.CharField(max_length=255)
    car_type = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'site_kcar_cars'


class TimeDealCarMpark(models.Model):
    id_car = models.CharField(max_length=255)
    url_car = models.URLField(max_length=255)
    car_mark = models.CharField(max_length=255)
    car_model = models.CharField(max_length=255)
    price = models.IntegerField()
    year = models.IntegerField()
    millage = models.IntegerField()
    car_fuel = models.CharField(max_length=255)
    car_color = models.CharField(max_length=255)
    car_noAccident = models.CharField(max_length=255)
    engine_capacity = models.IntegerField()
    car_type = models.CharField(max_length=255)
    transmission = models.CharField(max_length=255)
    main_image = models.CharField(max_length=255)
    images = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'site_mpark_cars'
