from sqlalchemy import Column, Integer, String, DateTime, select, func
from utils.request_api import fetch_page_data
from utils.log import logger
from bs4 import BeautifulSoup
import re
from datetime import datetime
from utils.db import Base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
import asyncio
from sqlalchemy.exc import SQLAlchemyError
import pytz

novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")


def get_novosibirsk_time():
    return datetime.now(novosibirsk_tz)


class TimeDealCar(Base):
    __tablename__ = 'site_bobaedream_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_car = Column(String)
    url_car = Column(String)
    car_mark = Column(String)
    car_model = Column(String)
    drive = Column(String)
    price = Column(String)
    year = Column(Integer)
    millage = Column(Integer)
    images = Column(String)
    main_image = Column(String)
    color = Column(String)
    transmission = Column(String)
    engine_capacity = Column(String)
    car_fuel = Column(String)
    created_at = Column(DateTime(timezone=True), default=get_novosibirsk_time, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_novosibirsk_time, onupdate=get_novosibirsk_time,
                        nullable=False)


async def parse_car_data(item):
    try:
        name = item.select_one(".tit.ellipsis a")
        name = name.get_text(strip=True) if name else None
        if name:
            car_full_name = name.split(" ")
            car_mark = car_full_name[0]
            car_model = " ".join(car_full_name[1:])
        else:
            car_mark = None
            car_model = None

        price = item.select_one(".mode-cell.price .price-whole")
        price = price.get_text(strip=True) if price else None

        photo = item.select_one(".thumb img")
        photo_url = f"https:{photo['src']}" if photo and 'src' in photo.attrs else None

        car_link = item.select_one(".tit.ellipsis a")
        car_link = car_link["href"] if car_link and 'href' in car_link.attrs else None

        car_id_match = re.search(r'no=(\d+)', car_link) if car_link else None
        car_id = car_id_match.group(1) if car_id_match else None

        url_car = f"https://www.bobaedream.co.kr/cyber/CyberCar_view.php?no={car_id}&gubun=I"

        return TimeDealCar(
            id_car=car_id,
            url_car=url_car,
            car_mark=car_mark,
            car_model=car_model,
            price=price,
            images=photo_url,
            main_image=photo_url
        )
    except Exception as e:
        logger.error(f"Ошибка парсинга автомобиля: {e}")
        return None


async def process_page(page, headers, async_session, session):
    data = await fetch_page_data(session, page, headers)
    if not data:
        return 0

    try:
        soup = BeautifulSoup(data["myvecTxt"], "html.parser")
        items = soup.select("li.product-item")
        if not items:
            return 0
    except Exception as e:
        logger.error(f"Ошибка парсинга HTML для страницы {page}: {e}")
        return 0

    tasks = [parse_car_data(item) for item in items]
    cars = [car for car in await asyncio.gather(*tasks) if car]

    async with async_session() as db_session:
        try:
            async with db_session.begin():
                existing_ids = {
                    car.id_car for car in await db_session.execute(
                        select(TimeDealCar.id_car)
                    )
                }
                for car in cars:
                    if car.id_car not in existing_ids:
                        db_session.add(car)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка сохранения данных в БД: {e}")
            await db_session.rollback()

    return len(cars)


async def process_page_limited(page, headers, async_session, session, semaphore):
    async with semaphore:
        return await process_page(page, headers, async_session, session)


async def process_cars():
    semaphore = asyncio.Semaphore(10)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
        'Referer': 'https://www.bobaedream.co.kr/cyber/CyberCar.php?sel_m_gubun=ALL'
    }

    engine = create_async_engine("sqlite+aiosqlite:///cars_2.db")
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        return

    async with aiohttp.ClientSession() as session:
        pages = list(range(1, 4000))
        tasks = [
            process_page_limited(page, headers, async_session, session, semaphore)
            for page in pages
        ]
        results = await asyncio.gather(*tasks)

    logger.info("Процесс обработки данных завершен.")


def main():
    asyncio.run(process_cars())


if __name__ == '__main__':
    main()
