from django.core.management.base import BaseCommand
from catalog.models import TimeDealCarMpark
from django.db.models import Count


class Command(BaseCommand):
    help = 'Подсчитывает уникальные значения для полей в модели TimeDealCar'

    def handle(self, *args, **kwargs):
        colors_count = (TimeDealCarMpark.objects
                        .values('transmission')  # Группируем по полю 'color'
                        .annotate(color_count=Count('transmission'))  # Подсчитываем количество для каждого цвета
                        .order_by('transmission'))  # Сортируем по цвету

        # Выводим результаты
        for color in colors_count:
            self.stdout.write(f"Тип КПП: {color['transmission']}, Количество: {color['color_count']}")
