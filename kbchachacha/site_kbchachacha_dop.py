import base64
import random
import ssl

from kbchachacha.site_kbchachacha import TimeDealCar
from utils.log import logger
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from aiohttp import ClientSession
from sqlalchemy import select
from bs4 import BeautifulSoup
import aiohttp


async def update_car_details(car_id, async_session, price, year, millage, car_fuel, transmission, car_type, color,
                             images,
                             main_image, engine_capacity):
    async with async_session() as session:
        try:
            car = await session.execute(
                select(TimeDealCar).filter_by(id_car=car_id)
            )
            car = car.scalars().first()
            if not car:
                logger.warning(f"Машина с id {car_id} не найдена.")
                return None

            car.transmission = transmission
            car.car_fuel = car_fuel
            car.images = images
            car.year = year
            car.millage = millage
            car.price = price
            car.color = color
            car.main_image = main_image
            car.car_type = car_type
            car.engine_capacity = engine_capacity

            await session.commit()
        except Exception as e:
            logger.warning(f"Ошибка обработки данных для {car.id_car}: {e}")
            await session.rollback()
            return None


def detect_captcha(response):
    soup = BeautifulSoup(response, "html.parser")
    scripts = soup.find_all("script")
    for script in scripts:
        if "src" in script.attrs:
            captcha = script["src"]
            if "recaptcha" in captcha:
                return True
    return False


async def request(http_session, url, retries=3):
    proxy_auth = aiohttp.BasicAuth("3nbFwoBiE8TZ", "RNW78Fm5")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.kbchachacha.com/",
        "Connection": "keep-alive"
    }

    for attempt in range(1, retries + 1):
        try:
            async with http_session.get(url, headers=headers, proxy="http://pool.proxy.market:10384",
                                        proxy_auth=proxy_auth, ssl=False, trust_env=True,
                                        timeout=100) as response:
                response.raise_for_status()
                text = await response.text()
                if detect_captcha(text):
                    await asyncio.sleep(2 ** attempt)
                else:
                    return text
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса к API: {e}")
            await asyncio.sleep(2 ** attempt)

    return None


def parse_html(response):
    soup = BeautifulSoup(response, "html.parser")
    price_tag = soup.find("div", class_="car-buy-price")
    if price_tag:
        price = price_tag.find("dt", string="판매가격")
        if price:
            price = price.find_next_sibling("dd").get_text(strip=True)
        else:
            price = None
    else:
        price = None

    table = soup.find("table", class_="detail-info-table")
    if not table:
        logger.warning("Не удалось найти таблицу с деталями автомобиля")
        return None

    year = table.find("th", string="연식")
    if year:
        year = year.find_next("td").get_text(strip=True)
    else:
        year = None

    millage = table.find("th", string="주행거리")
    if millage:
        millage = millage.find_next("td").get_text(strip=True)
    else:
        millage = None

    car_fuel = table.find("th", string="연료")
    if car_fuel:
        car_fuel = car_fuel.find_next("td").get_text(strip=True)
    else:
        car_fuel = None

    transmission = table.find("th", string="변속기")
    if transmission:
        transmission = transmission.find_next("td").get_text(strip=True)
    else:
        transmission = None

    car_type = table.find("th", string="차종")
    if car_type:
        car_type = car_type.find_next("td").get_text(strip=True)
    else:
        car_type = None

    color = table.find("th", string="색상")
    if color:
        color = color.find_next("td").get_text(strip=True)
    else:
        color = None

    engine_capacity = table.find("th", string="배기량")
    if engine_capacity:
        engine_capacity = engine_capacity.find_next("td").get_text(strip=True)
    else:
        engine_capacity = None

    images_tag = soup.find("div", class_="page01")
    images = []

    if images_tag:
        for image in images_tag.find_all("a"):
            img_tag = image.find("img")
            if img_tag and "src" in img_tag.attrs:
                images.append(img_tag["src"])

    if images:
        main_image = images[0]
    else:
        main_image = None

    images = ",".join(images)

    return price, year, millage, car_fuel, transmission, car_type, color, images, main_image, engine_capacity


async def process_car(http_session, async_session, car):
    url = f"https://www.kbchachacha.com/public/car/detail.kbc?carSeq={car.id_car}"
    response = await request(http_session, url)

    if response:
        parsed_data = parse_html(response)

        if parsed_data:
            price, year, millage, car_fuel, transmission, car_type, color, images, main_image, engine_capacity = parsed_data
            await update_car_details(car.id_car, async_session, price, year, millage, car_fuel, transmission, car_type,
                                     color,
                                     images, main_image, engine_capacity)
            print(f"Обновилась {car.id_car}")
        else:
            logger.warning(f"Не удалось извлечь данные для машины с id {car.id_car}.")
            return None
    else:
        logger.error(f"Ошибка при получении данных для машины с id {car.id_car}.")
        return None


async def limited_process_car(http_session, async_session_factory, car, semaphore):
    async with semaphore:
        async with async_session_factory() as async_session:
            await process_car(http_session, async_session, car)
            await asyncio.sleep(random.uniform(5, 10))


async def process_cars():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        limit_per_host=20,
    )
    semaphore = asyncio.Semaphore(10)
    async_engine = create_async_engine("sqlite+aiosqlite:///../cars_2.db")
    async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

    try:
        async with async_session() as session:
            result = await session.execute(select(TimeDealCar))
            cars = result.scalars().all()
    except Exception as e:
        logger.error(f"Ошибка извлечения данных из БД: {e}")
        return

    async with ClientSession(connector=connector) as http_session:
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
