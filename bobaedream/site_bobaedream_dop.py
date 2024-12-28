from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.log import logger
from bs4 import BeautifulSoup
from bobaedream.site_bobaedream import TimeDealCar
from utils.request_api import fetch_car_details
from sqlalchemy import select
import asyncio
import datetime
import re


def parse_car_details(html):
    soup = BeautifulSoup(html, "html.parser")
    try:
        table = soup.find("div", class_="info-basic").find("table")
        table_2 = soup.find("div", class_="wrap-detail-spec mode-n6")

        color = extract_table_value(table, "색상")
        transmission = extract_table_value(table, "변속기")
        engine_capacity = extract_table_value(table, "배기량")
        if engine_capacity:
            match = re.match(r"[\d,]+", engine_capacity)
            if match:
                engine_capacity = match.group(0)
                if ',' in engine_capacity:
                    engine_capacity = engine_capacity.replace(',', '')
                engine_capacity = int(engine_capacity)
        car_fuel = extract_table_value(table, "연료")
        year = extract_table_value(table, "연식")
        if year:
            match = re.match(r"\d+", year)
            if match:
                year = int(match.group(0))
        millage = extract_table_value(table, "주행거리")
        if millage:
            match = re.match(r"[\d,]+", millage)
            if match:
                millage = match.group(0)
                if ',' in millage:
                    millage = millage.replace(',', '')
                millage = int(millage)

        drive = extract_table2_value(table_2)

        return color, transmission, engine_capacity, car_fuel, year, millage, drive
    except AttributeError:
        logger.error("Не удалось найти таблицу с информацией о машине.")
        return None, None, None, None, None, None, None


def extract_table_value(table, field_name):
    th = table.find("th", string=field_name)
    return th.find_next("td").get_text(strip=True) if th else None


def extract_table2_value(table):
    dd = table.select_one("dd:has(span.ib-spec.ws)")
    strong = dd.select_one("strong.txt")
    if strong:
        value_dd = strong.get_text(strip=True)
    else:
        value_dd = None

    return value_dd


def update_car_details(car, color, transmission, engine_capacity, car_fuel, year, millage, drive):
    try:
        if color:
            car.color = color
        if transmission:
            car.transmission = transmission
        if engine_capacity:
            car.engine_capacity = engine_capacity
        if car_fuel:
            car.car_fuel = car_fuel
        if year:
            car.year = year
        if millage:
            car.millage = millage
        if drive:
            car.drive = drive
    except Exception as e:
        logger.error(f"Ошибка при обновлении параметров: {e}")


async def process_request_limited(car, semaphore, session_factory):
    async with semaphore:
        try:
            update_time = datetime.datetime.strftime(car.updated_at, "%Y-%m-%d")
            now_date = str(datetime.datetime.now().date())

            if update_time == now_date:
                car_details_html = await fetch_car_details(car.id_car)
            else:
                car_details_html = None
            if car_details_html:
                color, transmission, engine_capacity, car_fuel, year, millage, drive = parse_car_details(
                    car_details_html)
                async with session_factory() as db_session:
                    async with db_session.begin():
                        update_car_details(car, color, transmission, engine_capacity, car_fuel, year, millage, drive)

                        db_session.add(car)
                        await db_session.commit()
            await asyncio.sleep(1)
            return car
        except Exception as e:
            logger.error(f"Ошибка при обработке автомобиля {car.id_car}: {e}")
            return None


async def process_cars():
    try:
        semaphore = asyncio.Semaphore(10)

        engine = create_async_engine("sqlite+aiosqlite:///cars_2.db")
        session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

        async with session_factory() as db_session:
            async with db_session.begin():
                result = await db_session.execute(select(TimeDealCar))
                cars = result.scalars().all()

        tasks = [process_request_limited(car, semaphore, session_factory) for car in cars]
        await asyncio.gather(*tasks)

        logger.info("Процесс обновления данных завершен.")
    except Exception as e:
        logger.error(f"Ошибка обновления данных: {e}")


def main():
    asyncio.run(process_cars())


if __name__ == "__main__":
    main()
