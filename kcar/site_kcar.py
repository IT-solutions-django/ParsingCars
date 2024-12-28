from aiohttp import ClientSession
from sqlalchemy import Column, Integer, String, DateTime, select, func
import requests
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.log import logger
from utils.db import Base
import asyncio
import pytz

novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")


def get_novosibirsk_time():
    return datetime.now(novosibirsk_tz)


class TimeDealCar(Base):
    __tablename__ = 'site_kcar_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_car = Column(String)
    url_car = Column(String)
    car_model = Column(String)
    car_mark = Column(String)
    price = Column(Integer)
    main_image = Column(String)
    images = Column(String)
    year = Column(Integer)
    millage = Column(Integer)
    drive = Column(String)
    color = Column(String)
    car_fuel = Column(String)
    transmission = Column(String)
    car_noAccident = Column(String)
    car_type = Column(String)
    created_at = Column(DateTime(timezone=True), default=get_novosibirsk_time, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_novosibirsk_time, onupdate=get_novosibirsk_time,
                        nullable=False)


def fetch_car_data(url, headers, params):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к API: {e}")
        return None


async def request(url, data_post, page, http_session, headers):
    try:
        async with http_session.get(url, headers=headers, params=data_post, timeout=100) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса к API для {page}: {e}")
        return None


async def process_car_item(item):
    try:
        id_car = item.get("carCd")
        car_model = item.get("modelNm")
        car_name = item.get("mnuftrNm")
        price = item.get("prc")
        if price:
            price = int(price)
        image = item.get("lsizeImgPath")
        year = item.get("prdcnYr")
        if year:
            year = int(year)
        millage = item.get("milg")
        if millage:
            millage = int(millage)
        color = item.get("extrColorNm")
        url_car = f"https://www.kcar.com/bc/detail/carInfoDtl?i_sCarCd={id_car}"

        return TimeDealCar(
            id_car=id_car,
            url_car=url_car,
            car_model=car_model,
            car_mark=car_name,
            price=price,
            main_image=image,
            year=year,
            millage=millage,
            color=color,
        )
    except Exception as e:
        logger.warning(f"Ошибка обработки элемента данных: {item}. Ошибка: {e}")
        return None


async def save_cars_to_db_async(cars, async_session):
    async with async_session() as session:
        try:
            session.add_all(cars)
            await session.commit()
        except Exception:
            await session.rollback()
            return None


async def process_page(url, data_post, page, http_session, async_session_factory, existing_car, headers):
    response = await request(url, data_post, page, http_session, headers)

    if response:
        cars_list = response.get("data", {}).get("list", [])
        if not cars_list:
            return None
        cars = []
        for item in cars_list:
            cars.append(process_car_item(item))

        cars_add = await asyncio.gather(*cars)
        cars_add_new = [car for car in cars_add if car.id_car not in existing_car]

        await save_cars_to_db_async(cars_add_new, async_session_factory)
    else:
        return None


async def process_page_limited(url, data_post, page, http_session, async_session_factory, semaphore, existing_car,
                               headers):
    async with semaphore:
        await process_page(url, data_post, page, http_session, async_session_factory, existing_car, headers)
        await asyncio.sleep(1)


async def main():
    url = "https://api.kcar.com/bc/timeDealCar/list"
    page_size = 50
    total_pages = 500
    headers = {
        "Cookie": "ab.storage.deviceId.79570721-e48c-4ca4-b9d6-e036e9bfeff8=%7B%22g%22%3A%22b7404a2c-510b-12a8-560e-95604a58f89a%22%2C%22c%22%3A1732187811554%2C%22l%22%3A1732187811554%7D; ab.storage.sessionId.79570721-e48c-4ca4-b9d6-e036e9bfeff8=%7B%22g%22%3A%220eb30e25-7578-9663-a8fb-77a6be7f7ac7%22%2C%22e%22%3A1732190300903%2C%22c%22%3A1732187811597%2C%22l%22%3A1732188500903%7D;"
    }

    semaphore = asyncio.Semaphore(15)
    async_engine = create_async_engine("sqlite+aiosqlite:///cars_2.db")
    async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        return

    async with async_session() as session:
        result = await session.execute(
            select(TimeDealCar)
        )
        existing_car = result.scalars().all()

    existing_car_id = [car.id_car for car in existing_car]

    async with ClientSession() as http_session:
        tasks = []
        for page in range(1, total_pages + 1):
            params = {
                "currentPage": page,
                "pageSize": page_size,
                "creatYn": "N",
                "sIndex": 1,
                "eIndex": 10,
            }

            tasks.append(
                process_page_limited(url, params, page, http_session, async_session, semaphore, existing_car_id,
                                     headers))

        await asyncio.gather(*tasks)

    logger.info("Процесс обработки данных завершен.")


def main_run():
    asyncio.run(main())


if __name__ == '__main__':
    main_run()
