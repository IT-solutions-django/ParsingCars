import asyncio
import datetime
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from kcar.site_kcar import TimeDealCar
from utils.log import logger
from sqlalchemy import select
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
        details = car_details.get("data", {}).get("rvo", {})
        car_type = details.get("carctgr", None)
        car_transmission = details.get("trnsmsncdNm", None)
        car_fuel = details.get("fuelTypecdNm", None)
        car_noAccident = details.get("acdtHistComnt", None)
        drive = details.get("drvgYnNm", None)
        # engine_capacity = details.get('engdispmnt', None)

        images_list = [image["elanPath"] for image in car_details.get("data", {}).get("photoList", [])]
        res_images = ', '.join(images_list)

        car.transmission = car_transmission
        car.car_type = car_type
        car.car_fuel = car_fuel
        car.car_noAccident = car_noAccident
        car.drive = drive
        car.images = res_images

        session.add(car)
        await session.commit()
    except Exception as e:
        logger.warning(f"Ошибка обработки данных для {car.id_car}: {e}")
        await session.rollback()


async def request(url, http_session, id_car):
    random_user_agent = random.choice(user_agents)
    headers = {
        'User-Agent': random_user_agent,
        'Cookie': 'ab.storage.deviceId.79570721-e48c-4ca4-b9d6-e036e9bfeff8=%7B%22g%22%3A%22b7404a2c-510b-12a8-560e-95604a58f89a%22%2C%22c%22%3A1732187811554%2C%22l%22%3A1732187811554%7D; ab.storage.sessionId.79570721-e48c-4ca4-b9d6-e036e9bfeff8=%7B%22g%22%3A%220eb30e25-7578-9663-a8fb-77a6be7f7ac7%22%2C%22e%22%3A1732190300903%2C%22c%22%3A1732187811597%2C%22l%22%3A1732188500903%7D;',
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


async def process_car(http_session, session, car):
    url = f"https://api.kcar.com/bc/car-info-detail-of-ng?i_sCarCd={car.id_car}&i_sPassYn=N&bltbdKnd=CM050"

    update_time = datetime.datetime.strftime(car.updated_at, "%Y-%m-%d")
    now_date = str(datetime.datetime.now().date())

    if update_time == now_date:
        response = await request(url, http_session, car.id_car)
    else:
        response = None

    if response:
        await update_car_details(car, response, session)
    else:
        return None


async def limited_process_car(http_session, async_session_factory, car, semaphore):
    async with semaphore:
        async with async_session_factory() as session:
            await process_car(http_session, session, car)
            await asyncio.sleep(1)


async def process_cars():
    semaphore = asyncio.Semaphore(15)
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
