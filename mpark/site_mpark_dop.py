import datetime
import re
import aiohttp
import asyncio
from mpark.site_mpark import TimeDealCar
from utils.log import logger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

SEM_LIMIT = 10

unwanted_prefixes = [
    r"디 올 뉴", r"새로운", r"모든 새로운", r"올 뉴", r"그만큼",
    r"완전히 새로운", r"뉴", r"더 뉴", r"더 올 뉴", r"올뉴",
    r"올 뉴"
]

pattern = r"^(" + "|".join(unwanted_prefixes) + r")\s?"
brackets_pattern = r"(\s?\([^)]*\))$"


async def fetch_car_details_json(url, id_car, session, retries=5):
    delay = 1
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка при выполнении запроса к API для {id_car}: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
                delay *= 2
            else:
                logger.error("Превышено максимальное количество попыток.")
                return None
        except ValueError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return None


async def update_car_info(car, details):
    try:
        car_color = details.get("carColor", None)
        engine_capacity = details.get("numCc", None)
        car_type = details.get("carType", None)
        car_mark = details.get("carName", None)
        if car_mark:
            car_mark = car_mark.split(" ")[0]
        car_model = details.get("modelDetailName", None)
        if car_model:
            car_model = re.sub(pattern, "", car_model).strip()
            car_model = re.sub(brackets_pattern, "", car_model).strip()
        price = details.get("demoAmt", None)
        year = details.get("yymm", None)
        millage = details.get("km", None)
        car_fuel = details.get("carGas", None)
        car_noAccident = details.get("noAccident", None)
        transmission = details.get("carAutoGbn", None)
        images = details.get("images", [])
        image_urls = ",".join(images)
        main_image = images[0] if images else None

        car.car_color = car_color
        car.engine_capacity = engine_capacity
        car.car_type = car_type
        car.car_mark = car_mark
        car.car_model = car_model
        car.price = price
        car.year = year
        car.millage = millage
        car.car_fuel = car_fuel
        car.car_noAccident = car_noAccident
        car.transmission = transmission
        car.images = image_urls
        car.main_image = main_image
    except Exception as e:
        logger.error(f"Ошибка обработки данных для {car.id_car}: {e}")
        raise


async def process_car(session_factory, car, semaphore, client_session):
    url = f"https://api.m-park.co.kr/home/api/v1/wb/searchmycar/cardetailinfo/get?demoNo={car.id_car}"
    async with semaphore, session_factory() as session:
        update_time = datetime.datetime.strftime(car.updated_at, "%Y-%m-%d")
        now_date = str(datetime.datetime.now().date())

        if update_time == now_date:
            car_details = await fetch_car_details_json(url, car.id_car, client_session)
        else:
            car_details = None
        if car_details:
            try:
                details = car_details.get("data", {}).get("detailInfo", [])
                if not details:
                    return
                details = details[0]

                await update_car_info(car, details)
                session.add(car)
                await session.commit()
            except Exception as e:
                logger.error(f"Ошибка обновления данных для {car.id_car}: {e}")
                await session.rollback()


async def process_cars():
    engine = create_async_engine("sqlite+aiosqlite:///cars_2.db")
    try:
        session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with aiohttp.ClientSession() as client_session:
            async with session_factory() as session:
                async with session.begin():
                    result = await session.execute(select(TimeDealCar))
                    cars = result.scalars().all()

            semaphore = asyncio.Semaphore(SEM_LIMIT)
            tasks = [process_car(session_factory, car, semaphore, client_session) for car in cars]
            await asyncio.gather(*tasks)
    finally:
        await engine.dispose()


async def main():
    await process_cars()
    logger.info("Процесс обновления данных завершен.")


def main_run():
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
