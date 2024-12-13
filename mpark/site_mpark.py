import aiohttp
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, select, func
from utils.log import logger
from utils.db import Base
import pytz

novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")


def get_novosibirsk_time():
    return datetime.now(novosibirsk_tz)


class TimeDealCar(Base):
    __tablename__ = 'site_mpark_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_car = Column(String)
    url_car = Column(String)
    car_mark = Column(String)
    car_model = Column(String)
    price = Column(Integer)
    year = Column(Integer)
    millage = Column(Integer)
    car_fuel = Column(String)
    car_color = Column(String)
    car_noAccident = Column(String)
    engine_capacity = Column(Integer)
    car_type = Column(String)
    transmission = Column(String)
    main_image = Column(String)
    images = Column(String)
    created_at = Column(DateTime(timezone=True), default=get_novosibirsk_time, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_novosibirsk_time, onupdate=get_novosibirsk_time,
                        nullable=False)


DATABASE_URL = "sqlite+aiosqlite:///../cars_2.db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

SEMAPHORE_LIMIT = 10
semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)


async def initialize_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def fetch_data_from_api(url, retries=5):
    delay = 1
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=50)) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка при выполнении запроса к API: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
                delay *= 2
            else:
                logger.error("Превышено максимальное количество попыток.")
                return None
        except ValueError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return None


async def process_car_data(cars_list):
    tasks = []
    for item in cars_list:
        tasks.append(process_single_car(item))
    return await asyncio.gather(*tasks)


async def process_single_car(item):
    async with semaphore:
        try:
            id_car = item.get("demoNo")
            url_car = f"https://www.m-park.co.kr/buy/detail/{id_car}"
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(TimeDealCar).where(TimeDealCar.id_car == id_car))
                existing_car = result.scalars().first()

                if not existing_car:
                    new_car = TimeDealCar(id_car=id_car, url_car=url_car)
                    session.add(new_car)
                    await session.commit()
        except Exception as e:
            logger.error(f"Ошибка обработки элемента данных: {item}. Ошибка: {e}")


async def main():
    await initialize_database()

    url = "https://api.m-park.co.kr/home/api/v1/wb/searchmycar/carlistinfo/get?"
    data = await fetch_data_from_api(url)

    if data:
        cars_list = data.get("data", [])
        await process_car_data(cars_list)

    logger.info("Процесс обработки данных завершен.")


def main_run():
    asyncio.run(main())


if __name__ == '__main__':
    main_run()
