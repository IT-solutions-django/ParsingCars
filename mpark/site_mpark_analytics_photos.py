from mpark.site_mpark import TimeDealCar
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import asyncio
import aiohttp
from loguru import logger

logger.add("inaccessible_photos.log", rotation="10 MB", compression="zip", level="INFO")

engine = create_async_engine("sqlite+aiosqlite:///../cars_2.db")
session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def check_photo_url(session, url, semaphore, retries=3, min_size=10 * 1024):
    async with semaphore:
        for attempt in range(1, retries + 1):
            try:
                async with session.get(url, timeout=50) as response:
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        content_length = response.headers.get('Content-Length', None)
                        if 'image' in content_type:
                            size = int(content_length) if content_length else None
                            if not size:
                                logger.warning(f"Размер фото не представлен, считается неликвидным.")
                                return url, False, response.status
                            if size < min_size:
                                logger.warning(f"Фото {url} слишком маленькое ({size} байт), считается неликвидным.")
                                return url, False, response.status
                            return url, True, response.status
                        elif response.status == 503:
                            logger.warning(f"Сервер временно недоступен (503) для URL {url}, попытка {attempt}")
                            await asyncio.sleep(2 ** attempt)
                        else:
                            return url, False, response.status
                    else:
                        return url, False, response.status
            except Exception as e:
                logger.error(f"Ошибка при проверке URL {url}: {e}")
                return url, False, None

        return url, False, 503


async def request_photos(images):
    semaphore = asyncio.Semaphore(50)

    async with aiohttp.ClientSession() as session:
        tasks = [check_photo_url(session, url, semaphore) for url in images]
        results = await asyncio.gather(*tasks)

    accessible_photos = [(url, status) for url, is_accessible, status in results if is_accessible]
    inaccessible_photos = [(url, status) for url, is_accessible, status in results if not is_accessible]

    for url, status in inaccessible_photos:
        logger.info(f"Недоступное фото: {url}. Статус ответа - {status}")

    print(f"Доступные фотографии: {len(accessible_photos)}")
    print(f"Недоступные фотографии: {len(inaccessible_photos)}")

    return accessible_photos, inaccessible_photos


async def analytics_photos():
    async with session_factory() as db_session:
        async with db_session.begin():
            result = await db_session.execute(select(TimeDealCar))
            cars = result.scalars().all()

            images_all = []

            for column in TimeDealCar.__table__.columns:
                field_name = column.name
                if field_name in ("images",):
                    for car in cars:
                        if getattr(car, field_name):
                            car_images = getattr(car, field_name).split(',')
                            images_all.extend(car_images)

            await request_photos(images_all)


def main():
    asyncio.run(analytics_photos())


if __name__ == '__main__':
    main()
