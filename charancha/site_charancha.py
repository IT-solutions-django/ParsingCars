from aiohttp import ClientSession
from sqlalchemy import Column, Integer, String, DateTime, select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.log import logger
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from utils.db import Base
import asyncio

novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")


def get_novosibirsk_time():
    return datetime.now(novosibirsk_tz)


class TimeDealCar(Base):
    __tablename__ = 'site_charancha_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_car = Column(String)
    url_car = Column(String)
    car_mark = Column(String)
    car_model = Column(String)
    car_complectation = Column(String)
    car_type = Column(String)
    price = Column(String)
    year = Column(Integer)
    millage = Column(Integer)
    images = Column(String)
    main_image = Column(String)
    color = Column(String)
    transmission = Column(String)
    engine_capacity = Column(Integer)
    car_fuel = Column(String)
    car_description = Column(String)
    created_at = Column(DateTime(timezone=True), default=get_novosibirsk_time, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_novosibirsk_time, onupdate=get_novosibirsk_time,
                        nullable=False)


async def parse_car_data(item):
    try:
        full_id = item.get("id")
        if full_id and full_id.startswith("chr"):
            car_id = full_id[3:]
        else:
            car_id = full_id

        url_car = f"https://charancha.com/bu/sell/view?sellNo={car_id}"

        return TimeDealCar(
            id_car=car_id,
            url_car=url_car
        )
    except Exception:
        return None


async def save_cars_to_db_async(cars, async_session):
    async with async_session() as session:
        try:
            session.add_all(cars)
            await session.commit()
        except Exception:
            await session.rollback()
            return None


async def request(url, data_post, page, http_session):
    try:
        async with http_session.post(url, data=data_post, timeout=100) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса к API для {page}: {e}")
        return None


async def process_page(url, data_post, page, http_session, async_session, existing_car):
    response = await request(url, data_post, page, http_session)

    if response:
        try:
            soup = BeautifulSoup(response, 'html.parser')
            paginate_div = soup.find("div", class_="paginate")
            active_page = str(paginate_div.find("a", class_="active").text)
            if active_page != str(page):
                return None
            elements = soup.find_all('li', class_="cars__li")
            if not elements:
                return None
        except Exception as e:
            logger.error(f"Ошибка парсинга HTML для страницы {page}: {e}")
            return None

        cars = []
        for item in elements:
            cars.append(parse_car_data(item))

        cars_add = await asyncio.gather(*cars)

        cars_add_new = [car for car in cars_add if car.id_car not in existing_car]

        await save_cars_to_db_async(cars_add_new, async_session)
    else:
        return None


async def process_page_limited(url, data_post, page, http_session, async_session_factory, semaphore, existing_car):
    async with semaphore:
        await process_page(url, data_post, page, http_session, async_session_factory, existing_car)
        await asyncio.sleep(5)


async def process_cars():
    total_pages = 1000

    semaphore = asyncio.Semaphore(10)
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
            url = "https://charancha.com/bu/sell/pcListCtl"
            data_post = {
                "page": page
            }
            tasks.append(
                process_page_limited(url, data_post, page, http_session, async_session, semaphore, existing_car_id))

        await asyncio.gather(*tasks)

    logger.info("Процесс обработки данных завершен.")


def main():
    asyncio.run(process_cars())


if __name__ == '__main__':
    main()
