import asyncio
import datetime
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from kcar.site_kcar import TimeDealCar
from utils.log import logger
from sqlalchemy import select


async def update_car_details(car, car_details, session):
    try:
        details = car_details.get("data", {}).get("rvo", {})
        car_type = details.get("carctgr", None)
        car_transmission = details.get("trnsmsncdNm", None)
        car_fuel = details.get("fuelTypecdNm", None)
        car_noAccident = details.get("acdtHistComnt", None)
        drive = details.get("drvgYnNm", None)

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
    try:
        async with http_session.get(url, timeout=100) as response:
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
