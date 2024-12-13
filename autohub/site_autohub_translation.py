from autohub.site_autohub import TimeDealCar
from utils.log import logger
from utils.db import Session
from googletrans import Translator
import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

translator = Translator()

translations_words = {
    'color': {
        '': 'Не указан',
        '은회색': 'Серебристо-серый',
        '아이보리': 'Слоновая кость',
        '갈대색': 'Тростниковый',
        '청색': 'Синий',
        '화이트펄': 'Белый перламутр',
        '자주(보라)': 'Пурпурный (фиолетовый)',
        '초록(연두)': 'Зелёный (светло-зелёный)',
        '검정': 'Чёрный',
        '흰색(미색)': 'Белый (кремовый)',
        '회색': 'Серый',
        '파랑(남색,곤색)': 'Синий (тёмно-синий, васильковый)',
        '노랑': 'Жёлтый',
        '금모래': 'Золотой песок',
        '흰색': 'Белый',
        '베이지': 'Бежевый',
        '은색': 'Серебристый',
        '미색': 'Кремовый',
        '하늘': 'Небесно-голубой',
        '밀키베이지': 'Молочный бежевый',
        '플라티늄그라파이트': 'Платиновый графит',
        '다크그레이': 'Тёмно-серый',
        '그레이티타늄': 'Серый титан',
        '진주': 'Жемчужный',
        '쥐색': 'Мышиный серый',
        '갈색(밤색)': 'Коричневый (каштановый)',
        '빨강(주홍)': 'Красный (алый)',
        '-': 'Не применимо',
    },
    'transmission': {
        '': 'Не указана',
        '기타': 'Другое',
        '자동': 'Автоматическая',
        '수동': 'Механическая',
        '세미오토': 'Полуавтоматическая',
    },
    'car_fuel': {
        '': 'Не указан',
        '전기+경유': 'Электричество + дизель',
        '전기+휘발유': 'Электричество + бензин',
        '휘발유': 'Бензин',
        '전기': 'Электричество',
        '수소전기': 'Водородно-электрический',
        '전기+LPG': 'Электричество + LPG',
        '경유': 'Дизель',
        'LPG겸용': 'Сочетание LPG',
        'LPG': 'LPG',
    }
}


def translate_with_redis_cache(text, src, dest):
    if not text.strip():
        return text

    cache_key = f"{src}-{dest}:{text}"
    cached_value = redis_client.get(cache_key)
    if cached_value:
        return cached_value

    translated_text = translator.translate(text, src=src, dest=dest).text
    redis_client.set(cache_key, translated_text)
    return translated_text


def translation(car):
    try:
        fields_to_translate_ru = ["year", "color", "transmission", "car_fuel"]
        fields_to_translate_en = ["car_name"]

        for field in fields_to_translate_ru:
            value = getattr(car, field, None)
            if value and isinstance(value, str) and value.strip():
                translated_value = translate_with_redis_cache(value, src="ko", dest="ru")
                setattr(car, field, translated_value)

        for field in fields_to_translate_en:
            value = getattr(car, field, None)
            if value and isinstance(value, str) and value.strip():
                translated_value = translate_with_redis_cache(value, src="ko", dest="en")
                setattr(car, field, translated_value)

        return car
    except Exception as e:
        logger.error(f"Ошибка перевода для машины с ID {car.id}: {e}")
        return None


def process_cars(batch_size=100):
    session = Session()
    try:
        offset = 0
        while True:
            cars = session.query(TimeDealCar).limit(batch_size).offset(offset).all()
            if not cars:
                break
            for car in cars:
                car_translation = translation(car)
                if car_translation:
                    session.add(car_translation)
            session.commit()
            offset += batch_size
    except Exception as e:
        logger.error(f"Ошибка перевода автомобилей: {e}")
    finally:
        session.close()


def main():
    process_cars()
    logger.info("Процесс перевода данных завершен.")


if __name__ == "__main__":
    main()
