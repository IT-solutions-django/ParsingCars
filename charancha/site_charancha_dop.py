import asyncio
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from charancha.site_charancha import TimeDealCar
from utils.log import logger
from sqlalchemy import select
import datetime
import random

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.121 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.119 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'
]


async def update_car_details(car, car_details, session):
    try:
        details = car_details
        car_mark = details.get("makerNm", "")
        car_model = details.get("modelNm", "")
        car_complectation = details.get("gradeNm", "")
        price = details.get("sellPrice")
        if price:
            price = int(price)
        car_fuel = details.get("fuelNm", "")
        transmission = details.get("transmissionNm", "")
        millage = details.get("mileage", "")
        if millage:
            millage = int(millage)
        car_type = details.get("carTypeNm", "") + " " + details.get("bodyTypeNm", "")
        color = details.get("colorNm", "")
        images = details.get("carImg", "")
        main_image = images
        car_description = details.get("description", "")
        year = details.get("modelYyyyDt", "")
        if year:
            year = int(year)
        engine_capacity = details.get("displacement", "")
        if engine_capacity:
            engine_capacity = int(engine_capacity)

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
    random_user_agent = random.choice(user_agents)
    headers = {
        'User-Agent': random_user_agent,
        'Referer': 'https://charancha.com/bu/sell/view?sellNo=199fbf8a-c41d-11ef-a7c4-87395dc696bc',
        'Cookie': 'AWSALB=Fi6d3ztTcWNm2rv5JyahhP+JM8ZeGH3dBRLe5XECkrSe5j9wLAKKjX6nRIHcEtt2U2Ua+aP2E3byhvqxxT63sRUAcdJ3wEvF65youuKm2ixeVGHtEy8MwIvjzbA3; AWSALBCORS=Fi6d3ztTcWNm2rv5JyahhP+JM8ZeGH3dBRLe5XECkrSe5j9wLAKKjX6nRIHcEtt2U2Ua+aP2E3byhvqxxT63sRUAcdJ3wEvF65youuKm2ixeVGHtEy8MwIvjzbA3',
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
    try:
        async with http_session.get(url, timeout=180, headers=headers) as response:
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
            await asyncio.sleep(3)


async def process_cars():
    semaphore = asyncio.Semaphore(10)
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
