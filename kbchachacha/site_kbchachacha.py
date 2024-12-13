import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, select
from datetime import datetime
from utils.log import logger
from utils.db import Base


class TimeDealCar(Base):
    __tablename__ = 'site_kbchachacha_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_car = Column(String)
    url_car = Column(String)
    car_mark = Column(String)
    car_model = Column(String)
    price = Column(Integer)
    main_image = Column(String)
    images = Column(String)
    year = Column(Integer)
    millage = Column(Integer)
    color = Column(String)
    car_fuel = Column(String)
    car_type = Column(String)
    transmission = Column(String)
    engine_capacity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


async def fetch_car_data(url, session):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса к API: {e}")
        return None


def process_car_item(id_car, car_name):
    url_car = f"https://www.kbchachacha.com/public/car/detail.kbc?carSeq={id_car}"
    if car_name:
        car_full_name = car_name.split(" ")
        car_mark = car_full_name[0]
        car_model = " ".join(car_full_name[1:])
    else:
        car_mark = None
        car_model = None
    try:
        return TimeDealCar(
            id_car=id_car,
            car_mark=car_mark,
            car_model=car_model,
            url_car=url_car
        )
    except Exception as e:
        logger.warning(f"Ошибка обработки элемента данных для {id_car}. Ошибка: {e}")
        return None


async def process_page(page, http_session, async_session):
    url = f"https://www.kbchachacha.com/public/search/list.empty?page={page}&sort=-orderDate&_pageSize=3&pageSize=4"
    data = await fetch_car_data(url, http_session)
    if not data:
        return []

    try:
        soup = BeautifulSoup(data, "html.parser")
        cars = soup.find_all('div', class_='area')
        if not cars:
            return []

        car_data = []
        for car in cars:
            car_id = car.get('data-car-seq')
            title_tag = car.find('strong', class_='tit')
            car_title = title_tag.get_text(strip=True) if title_tag else None
            car_data.append({'id': car_id, 'title': car_title})

        async def process_car(item):
            car_new = process_car_item(item["id"], item["title"])
            if car_new:
                async with async_session() as session:
                    result = await session.execute(
                        select(TimeDealCar).filter_by(id_car=car_new.id_car)
                    )
                    existing_car = result.scalars().first()
                    if not existing_car:
                        session.add(car_new)
                        await session.commit()
                        return car_new
            return None

        tasks = [process_car(item) for item in car_data]
        processed_cars = await asyncio.gather(*tasks)
        return [car for car in processed_cars if car]

    except Exception as e:
        logger.error(f"Ошибка парсинга HTML для страницы {page}: {e}")
        return []


async def process_page_limited(page, http_session, session, semaphore):
    async with semaphore:
        cars = await process_page(page, http_session, session)
        if cars:
            await save_cars_to_db_async(cars, session)
        return cars


async def save_cars_to_db_async(cars, async_session):
    async with async_session() as session:
        try:
            session.add_all(cars)
            await session.commit()
        except Exception:
            await session.rollback()


async def main():
    semaphore = asyncio.Semaphore(10)
    total_pages = 1000
    async_engine = create_async_engine("sqlite+aiosqlite:///../cars_2.db")
    async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("База данных успешно инициализирована.")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        return

    async with ClientSession() as http_session:
        tasks = []
        for page in range(1, total_pages + 1):
            tasks.append(process_page_limited(page, http_session, async_session, semaphore))

        await asyncio.gather(*tasks)

    logger.info("Процесс обработки данных завершен.")


if __name__ == '__main__':
    asyncio.run(main())
