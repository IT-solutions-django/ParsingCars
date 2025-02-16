import aiohttp
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, select
from utils.log import logger
from utils.db import Base
import pytz
import random

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.121 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.119 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'
]

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


DATABASE_URL = "sqlite+aiosqlite:///cars_2.db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

SEMAPHORE_LIMIT = 10
semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)


async def initialize_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def fetch_data_from_api(url, retries=5):
    random_user_agent = random.choice(user_agents)
    headers = {
        'User-Agent': random_user_agent,
        'Referer': 'https://www.m-park.co.kr/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'DNT': '1'
    }
    delay = 1
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=180), headers=headers) as response:
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
