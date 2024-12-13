import asyncio
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from charancha.site_charancha import TimeDealCar
from utils.log import logger
from sqlalchemy import select
import datetime


async def update_car_details(car, car_details, session):
    try:
        details = car_details
        car_mark = details.get("makerNm", "")
        car_model = details.get("modelNm", "")
        car_complectation = details.get("gradeNm", "")
        price = details.get("sellPrice")
        car_fuel = details.get("fuelNm", "")
        transmission = details.get("transmissionNm", "")
        millage = details.get("mileage", "")
        car_type = details.get("carTypeNm", "") + " " + details.get("bodyTypeNm", "")
        color = details.get("colorNm", "")
        images = details.get("carImg", "")
        main_image = images
        car_description = details.get("description", "")
        year = details.get("modelYyyyDt", "")
        engine_capacity = details.get("displacement", "")

        car.car_mark = car_mark
        car.car_model = car_model
        car.car_complectation = car_complectation
        car.price = price
        car.car_fuel = car_fuel
        car.transmission = transmission
        car.millage = millage
        car.car_type = car_type
        car.color = color
        car.images = images
        car.main_image = main_image
        car.car_description = car_description
        car.year = year
        car.engine_capacity = engine_capacity

        session.add(car)
        await session.commit()
    except Exception as e:
        logger.warning(f"Ошибка обработки данных для {car.id_car}: {e}")
        await session.rollback()
        return None


async def request(http_session, url, id_car):
    try:
        async with http_session.get(url, timeout=30) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса к API для {id_car}: {e}")
        return None


async def process_car(http_session, async_session, car):
    url = f"https://charancha.com/v1/cars/{car.id_car}?"

    update_time = datetime.datetime.strftime(car.updated_at, "%Y-%m-%d")
    now_date = str(datetime.datetime.now().date())

    if update_time == now_date:
        response = await request(http_session, url, car.id_car)
    else:
        response = None

    if response:
        car_update = await update_car_details(car, response, async_session)
        return car_update
    else:
        return None


async def limited_process_car(http_session, async_session_factory, car, semaphore):
    async with semaphore:
        async with async_session_factory() as session:
            await process_car(http_session, session, car)


async def process_cars():
    semaphore = asyncio.Semaphore(50)
    async_engine = create_async_engine("sqlite+aiosqlite:///cars_2.db")
    async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

    try:
        async with async_session() as session:
            result = await session.execute(select(TimeDealCar))
            cars = result.scalars().all()
    except Exception as e:
        logger.error(f"Ошибка извлечения данных из БД: {e}")
        return

    async with ClientSession() as http_session:
        try:
            tasks = [limited_process_car(http_session, async_session, car, semaphore) for car in cars]
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Ошибка при обработке машин: {e}")
            return


def main():
    asyncio.run(process_cars())
    logger.info("Процесс обновления данных завершен.")


if __name__ == "__main__":
    main()
