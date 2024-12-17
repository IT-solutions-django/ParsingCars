from autohub.site_autohub import TimeDealCar
from utils.log import logger
import redis
import httpx
from googletrans import Translator
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

redis_client = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)


class AsyncTranslator(Translator):
    def __init__(self, max_concurrent_requests=5):
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def translate(self, text, src="auto", dest="en"):
        await asyncio.sleep(0.2)
        async with self.semaphore:
            async with httpx.AsyncClient() as client:
                data = await client.post(
                    "https://translate.googleapis.com/translate_a/single",
                    params={
                        "client": "gtx",
                        "sl": src,
                        "tl": dest,
                        "dt": "t",
                        "q": text,
                    },
                )
                data.raise_for_status()
                translation = data.json()[0][0][0]
                return translation


async def translate_with_redis_cache(translator, text, src, dest):
    if not text.strip():
        return text

    cache_key = f"{src}-{dest}:{text}"
    cached_value = redis_client.get(cache_key)
    if cached_value:
        return cached_value

    translated_text = await translator.translate(text, src=src, dest=dest)
    redis_client.set(cache_key, translated_text)
    return translated_text


async def translation(car, translator):
    try:
        fields_to_translate_ru = ["color", "transmission", "car_fuel"]
        fields_to_translate_en = ["car_mark", "car_model"]

        for field in fields_to_translate_ru:
            value = getattr(car, field, None)
            if value and isinstance(value, str) and value.strip():
                translated_value = await translate_with_redis_cache(translator, value, src="ko", dest="ru")
                setattr(car, field, translated_value)

        for field in fields_to_translate_en:
            value = getattr(car, field, None)
            if value and isinstance(value, str) and value.strip():
                translated_value = await translate_with_redis_cache(translator, value, src="ko", dest="en")
                setattr(car, field, translated_value)

        return car
    except Exception as e:
        logger.error(f"Ошибка перевода для машины с ID {car.id}: {e}")
        return None


async def process_cars(batch_size=100):
    engine = create_async_engine("sqlite+aiosqlite:///cars_2.db")
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        translator = AsyncTranslator()
        offset = 0

        while True:
            cars = await session.execute(
                select(TimeDealCar).limit(batch_size).offset(offset)
            )
            cars = cars.scalars().all()

            if not cars:
                break

            for car in cars:
                car_translation = await translation(car, translator)
                if car_translation:
                    await session.merge(car_translation)

            await session.commit()
            offset += batch_size


async def main():
    await process_cars()
    logger.info("Процесс перевода данных завершен.")


if __name__ == "__main__":
    asyncio.run(main())
