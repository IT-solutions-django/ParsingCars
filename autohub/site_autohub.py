import aiohttp
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from utils.log import logger
from bs4 import BeautifulSoup
from datetime import datetime
from utils.db import Base
from urllib.parse import parse_qs, urlparse
from sqlalchemy.exc import SQLAlchemyError
import re
import pytz

unwanted_prefixes = [
    r"디 올 뉴", r"새로운", r"모든 새로운", r"올 뉴", r"그만큼",
    r"완전히 새로운", r"뉴", r"더 뉴", r"더 올 뉴", r"올뉴"
]

pattern = r"^(" + "|".join(unwanted_prefixes) + r")\s?"
brackets_pattern = r"(\s?\([^)]*\))$"

novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")


def get_novosibirsk_time():
    return datetime.now(novosibirsk_tz)


class TimeDealCar(Base):
    __tablename__ = 'site_autohub_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_car = Column(String)
    url_car = Column(String)
    car_mark = Column(String)
    car_model = Column(String)
    price = Column(String)
    year = Column(Integer)
    millage = Column(Integer)
    images = Column(String)
    main_image = Column(String)
    color = Column(String)
    transmission = Column(String)
    engine_capacity = Column(String)
    car_fuel = Column(String)
    car_description = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, default=get_novosibirsk_time)
    updated_at = Column(DateTime(timezone=True), onupdate=get_novosibirsk_time, nullable=False,
                        default=get_novosibirsk_time)


async def fetch_page(session, url, id_car=None):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка при выполнении запроса к API для {id_car}: {e}")
        return None


async def fetch_car_detail_dop(session, id_car):
    url = f"http://www.autohub.co.kr/buy/detailView.asp?DemoNo={id_car}"
    html = await fetch_page(session, url, id_car)
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')
    info_detail = soup.select_one('.info-detail')
    engine_capacity = (
        info_detail.find("dt", string="배기량").find_next_sibling("dd").text
        if info_detail else None
    )
    if engine_capacity:
        match = re.match(r"[\d,]+", engine_capacity)
        if match:
            engine_capacity = match.group(0)
            if ',' in engine_capacity:
                engine_capacity = engine_capacity.replace(',', '')
            engine_capacity = int(engine_capacity)
    return engine_capacity


async def parse_car_data(session, item):
    try:
        url_car = "www.autohub.co.kr" + item['onclick'].split("'")[1]

        parsed_url = urlparse(url_car)
        query_params = parse_qs(parsed_url.query)
        car_id = query_params.get('DemoNo', [None])[0]

        car_name = item.select_one('.car-name em b').get_text(strip=True) if item.select_one('.car-name em b') else None
        if car_name:
            full_car_name = car_name.split(" ")
            car_mark = full_car_name[0]
            car_model = " ".join(full_car_name[1:])
            car_model = re.sub(pattern, "", car_model).strip()
            car_model = re.sub(brackets_pattern, "", car_model).strip()
        else:
            car_mark = None
            car_model = None
        car_price = item.select_one('.car-price b').get_text(strip=True) if item.select_one('.car-price b') else None
        if car_price:
            if not any(char.isalpha() for char in car_price):
                if ',' in car_price:
                    car_price = car_price.replace(',', '')
                car_price = int(car_price)
        car_description = item.select_one('.car-name span').get_text(strip=True) if item.select_one(
            '.car-name span') else None

        year = item.select_one('.car-state dt:-soup-contains("연식") + dd').get_text(strip=True) if item.select_one(
            '.car-state dt:-soup-contains("연식") + dd') else None
        if year:
            match = re.match(r"(\d+)", year)
            if match:
                year = int(match.group(1))
        millage = item.select_one('.car-state dt:-soup-contains("주행거리") + dd').get_text(strip=True) if item.select_one(
            '.car-state dt:-soup-contains("주행거리") + dd') else None
        if millage:
            match = re.match(r"[\d,]+", millage)
            if match:
                millage = match.group(0)
                if ',' in millage:
                    millage = millage.replace(',', '')
                millage = int(millage)

        color = item.select_one('.car-data dt:-soup-contains("색상") + dd').get_text(strip=True) if item.select_one(
            '.car-data dt:-soup-contains("색상") + dd') else None
        car_fuel = item.select_one('.car-data dt:-soup-contains("연료") + dd').get_text(strip=True) if item.select_one(
            '.car-data dt:-soup-contains("연료") + dd') else None
        transmission = item.select_one('.car-data dt:-soup-contains("변속기") + dd').get_text(
            strip=True) if item.select_one('.car-data dt:-soup-contains("변속기") + dd') else None

        images_list = [
            img['style'].split("url('")[1].split("')")[0]
            for img in item.select('.file-image p[style]')
            if "background-image" in img['style']
        ]

        main_image = images_list[0] if images_list else None
        images = ", ".join(images_list)

        engine_capacity = await fetch_car_detail_dop(session, car_id)

        return TimeDealCar(
            id_car=car_id,
            url_car=url_car,
            car_mark=car_mark,
            car_model=car_model,
            price=car_price,
            year=year,
            millage=millage,
            images=images,
            main_image=main_image,
            engine_capacity=engine_capacity,
            color=color,
            car_fuel=car_fuel,
            transmission=transmission,
            car_description=car_description
        )
    except Exception as e:
        logger.error(f"Ошибка парсинга данных автомобиля: {e}")
        return None


async def process_cars():
    engine = create_async_engine("sqlite+aiosqlite:///cars_2.db")
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        return

    async with aiohttp.ClientSession() as session:
        page = 1
        url = "http://www.autohub.co.kr/buy/proc/carList_proc.asp?"

        while True:
            data_post = {"gotoPage": page}
            max_retries = 3

            for attempt in range(max_retries):
                try:
                    async with session.post(url, data=data_post) as response:
                        response.raise_for_status()
                        html = await response.text()
                        break
                except aiohttp.ClientError as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Все попытки запроса страницы {page} исчерпаны. Пропускаем страницу.")
                        html = None
                        break
                    await asyncio.sleep(2)

            if not html:
                page += 1
                continue

            soup = BeautifulSoup(html, 'html.parser')
            elements = soup.find_all('li', onclick=True)
            if not elements:
                break

            tasks = [parse_car_data(session, item) for item in elements]
            cars = [car for car in await asyncio.gather(*tasks) if car]

            async with async_session() as db_session:
                if not cars:
                    return

                try:
                    async with db_session.begin():
                        existing_ids = {
                            row.id_car for row in await db_session.execute(
                                select(TimeDealCar.id_car).where(TimeDealCar.id_car.in_([car.id_car for car in cars]))
                            )
                        }
                except SQLAlchemyError as e:
                    logger.error(f"Ошибка при проверке существующих идентификаторов: {e}")
                    break

                new_cars = [car for car in cars if car.id_car not in existing_ids]

                if not new_cars:
                    break

                try:
                    async with db_session.begin():
                        db_session.add_all(new_cars)
                except SQLAlchemyError as e:
                    logger.error(f"Ошибка сохранения данных в БД: {e}")
                    await db_session.rollback()
                finally:
                    await db_session.close()

            page += 1

    logger.info("Процесс обработки данных завершен.")


def main():
    asyncio.run(process_cars())


if __name__ == '__main__':
    main()
